"""MCP server entrypoint."""

from fastmcp import FastMCP
from pydantic import ValidationError

from project.database import get_database
from project.embeddings import get_embedding_service
from project.errors import AppError
from project.models import (
    AppDependencies,
    CreateUserResponse,
    ErrorResponse,
    GetUserRequest,
    SearchUserMatch,
    SearchUsersRequest,
    UserCreate,
    UserRecord,
)
from project.vector_store import get_vector_store


def build_dependencies() -> AppDependencies:
    """Assemble the services the application will use."""
    return AppDependencies(
        database=get_database(),
        embedding_service=get_embedding_service(),
        vector_store=get_vector_store(),
    )


def initialize_runtime(dependencies: AppDependencies) -> None:
    """Initialize local runtime resources required by the MCP server."""
    dependencies.database.initialize()
    dependencies.vector_store.ensure_storage()


def register_tools(app: FastMCP, dependencies: AppDependencies) -> FastMCP:
    """Register MCP tools on the application instance."""

    @app.tool(
        name="create_user",
        description="Create a CRM user, persist it in SQLite, generate an embedding, and index it in FAISS.",
    )
    def create_user_tool(name: str, email: str, description: str) -> CreateUserResponse | ErrorResponse:
        """Persist a user and index its description embedding."""
        try:
            return create_user_workflow(name=name, email=email, description=description, dependencies=dependencies)
        except AppError as exc:
            return build_error_response(exc)

    @app.tool(
        name="search_users",
        description="Search for semantically similar CRM users using the FAISS index.",
    )
    def search_users_tool(query: str, top_k: int = 5) -> list[SearchUserMatch] | ErrorResponse:
        """Return the users most similar to the provided semantic query."""
        try:
            return search_users_semantic(query=query, top_k=top_k, dependencies=dependencies)
        except AppError as exc:
            return build_error_response(exc)

    @app.tool(
        name="get_user",
        description="Fetch a CRM user by ID from SQLite storage.",
    )
    def get_user_tool(user_id: int) -> UserRecord | ErrorResponse:
        """Return a persisted user by its identifier."""
        try:
            return get_user_workflow(user_id=user_id, dependencies=dependencies)
        except AppError as exc:
            return build_error_response(exc)

    return app


def create_app(dependencies: AppDependencies | None = None) -> FastMCP:
    """Return the configured MCP application."""
    deps = dependencies or build_dependencies()
    initialize_runtime(deps)
    app = FastMCP("crm-semantic-search")
    return register_tools(app, deps)


def create_user_workflow(
    name: str,
    email: str,
    description: str,
    dependencies: AppDependencies | None = None,
) -> CreateUserResponse:
    """Execute the full create-user workflow used by the MCP tool."""
    deps = dependencies or build_dependencies()
    try:
        payload = UserCreate(name=name, email=email, description=description)
    except ValidationError as exc:
        raise AppError("validation_error", exc.errors()[0]["msg"]) from exc

    created_user = deps.database.create_user(payload)
    try:
        description_embedding = deps.embedding_service.embed_description(created_user.description)
    except ValueError as exc:
        raise AppError("embedding_error", str(exc)) from exc

    deps.vector_store.add_vector(created_user.id, description_embedding)
    return CreateUserResponse(id=created_user.id)


def search_users_semantic(
    query: str,
    top_k: int,
    dependencies: AppDependencies | None = None,
) -> list[SearchUserMatch]:
    """Run the semantic search flow from query embedding to hydrated users."""
    deps = dependencies or build_dependencies()
    try:
        request = SearchUsersRequest(query=query, top_k=top_k)
    except ValidationError as exc:
        raise AppError("validation_error", exc.errors()[0]["msg"]) from exc

    try:
        query_embedding = deps.embedding_service.embed_query(request.query)
    except ValueError as exc:
        raise AppError("embedding_error", str(exc)) from exc

    vector_ids, scores = deps.vector_store.search(query_embedding, top_k=request.top_k)
    user_ids = deps.vector_store.get_user_ids_for_vectors(vector_ids)
    aligned_scores = scores[: len(user_ids)]
    return deps.database.hydrate_search_matches(user_ids, aligned_scores)


def get_user_workflow(user_id: int, dependencies: AppDependencies | None = None) -> UserRecord:
    """Return one persisted user or raise a consistent not-found error."""
    deps = dependencies or build_dependencies()
    try:
        request = GetUserRequest(user_id=user_id)
    except ValidationError as exc:
        raise AppError("validation_error", exc.errors()[0]["msg"]) from exc

    user = deps.database.get_user_by_id(request.user_id)
    if user is None:
        raise AppError("not_found", f"User with id={user_id} was not found.")
    return user


def build_error_response(error: AppError) -> ErrorResponse:
    """Convert an application error into the shared MCP response shape."""
    return ErrorResponse(code=error.code, message=error.message)


def run() -> None:
    """Start the MCP server runtime."""
    create_app().run()


if __name__ == "__main__":
    run()

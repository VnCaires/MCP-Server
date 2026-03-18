"""MCP server entrypoint."""

from fastmcp import FastMCP

from project.database import get_database
from project.embeddings import get_embedding_service
from project.models import AppDependencies, SearchUserMatch
from project.vector_store import get_vector_store


def build_dependencies() -> AppDependencies:
    """Assemble the services the application will use."""
    return AppDependencies(
        database=get_database(),
        embedding_service=get_embedding_service(),
        vector_store=get_vector_store(),
    )


def create_app() -> FastMCP:
    """Return the configured MCP application."""
    dependencies = build_dependencies()
    dependencies.database.initialize()
    dependencies.vector_store.ensure_storage()
    app = FastMCP("crm-semantic-search")
    return app


def search_users_semantic(
    query: str,
    top_k: int,
    dependencies: AppDependencies | None = None,
) -> list[SearchUserMatch]:
    """Run the semantic search flow from query embedding to hydrated users."""
    deps = dependencies or build_dependencies()
    query_embedding = deps.embedding_service.embed_query(query)
    vector_ids, scores = deps.vector_store.search(query_embedding, top_k=top_k)
    user_ids = deps.vector_store.get_user_ids_for_vectors(vector_ids)
    aligned_scores = scores[: len(user_ids)]
    return deps.database.hydrate_search_matches(user_ids, aligned_scores)


if __name__ == "__main__":
    create_app().run()

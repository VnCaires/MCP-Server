"""MCP server entrypoint."""

from fastmcp import FastMCP

from project.database import get_database
from project.embeddings import get_embedding_service
from project.models import AppDependencies
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


if __name__ == "__main__":
    create_app().run()

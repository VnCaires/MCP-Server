"""MCP server entrypoint."""

from fastmcp import FastMCP


mcp = FastMCP("crm-semantic-search")


def create_app() -> FastMCP:
    """Return the configured MCP application."""
    return mcp


if __name__ == "__main__":
    create_app().run()


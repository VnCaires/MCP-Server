"""Shared application error types."""


class AppError(Exception):
    """Typed application error used to build consistent MCP responses."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


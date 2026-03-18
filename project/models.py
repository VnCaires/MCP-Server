"""Application data models and MCP tool contracts."""

from dataclasses import dataclass
from typing import Literal

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    """Payload used to create a user."""

    name: str = Field(..., min_length=1)
    email: EmailStr
    description: str = Field(..., min_length=1)


class UserRecord(UserCreate):
    """User representation persisted in storage."""

    id: int

    @classmethod
    def from_row(cls, row: dict[str, object]) -> "UserRecord":
        """Build a user record from a SQLite row-like mapping."""
        return cls(
            id=int(row["id"]),
            name=str(row["name"]),
            email=str(row["email"]),
            description=str(row["description"]),
        )


class SearchUsersRequest(BaseModel):
    """Input contract for the `search_users` MCP tool."""

    query: str = Field(..., min_length=1)
    top_k: int = Field(default=5, ge=1)


class SearchUserMatch(UserRecord):
    """Single semantic search result item."""

    score: float


class GetUserRequest(BaseModel):
    """Input contract for the `get_user` MCP tool."""

    user_id: int = Field(..., ge=1)


class CreateUserResponse(BaseModel):
    """Output contract for the `create_user` MCP tool."""

    id: int


class ErrorResponse(BaseModel):
    """Shared error response shape for MCP tool failures."""

    code: Literal["not_found", "validation_error", "storage_error", "embedding_error"]
    message: str


@dataclass(frozen=True)
class AppDependencies:
    """Application dependency container used by the MCP server."""

    database: object
    embedding_service: object
    vector_store: object

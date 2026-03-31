"""Application data models and MCP tool contracts."""

from dataclasses import dataclass
from typing import Literal

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):

    name: str = Field(..., min_length=1)
    email: EmailStr
    description: str = Field(..., min_length=1)


class UserRecord(UserCreate):

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

    query: str = Field(..., min_length=1)
    top_k: int = Field(default=5, ge=1)


class SearchUserMatch(UserRecord):

    score: float


class VectorIndexEntry(BaseModel):

    vector_id: int = Field(..., ge=0)
    user_id: int = Field(..., ge=1)


class GetUserRequest(BaseModel):

    user_id: int = Field(..., ge=1)


class CreateUserResponse(BaseModel):

    id: int


class ErrorResponse(BaseModel):

    code: Literal["not_found", "validation_error", "storage_error", "embedding_error"]
    message: str


@dataclass(frozen=True)
class AppDependencies:

    database: object
    embedding_service: object
    vector_store: object

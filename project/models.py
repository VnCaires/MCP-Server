"""Application data models and MCP tool contracts."""

from dataclasses import dataclass
from typing import Literal

from pydantic import BaseModel, EmailStr, Field, field_validator


class UserCreate(BaseModel):

    name: str = Field(..., min_length=1)
    email: EmailStr
    description: str = Field(..., min_length=1)

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip().lower()
        return value

    @field_validator("email")
    @classmethod
    def validate_email_policy(cls, value: EmailStr) -> EmailStr:
        local_part = str(value).split("@", 1)[0]
        if "+" in local_part:
            raise ValueError("Plus aliases are not allowed in email addresses.")
        return value


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

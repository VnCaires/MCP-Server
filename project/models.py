"""Application data models."""

from dataclasses import dataclass

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    description: str


class UserRecord(UserCreate):
    id: int


@dataclass(frozen=True)
class AppDependencies:
    """Application dependency container used by the MCP server."""

    database: object
    embedding_service: object
    vector_store: object


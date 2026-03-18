"""Application data models."""

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    description: str


class UserRecord(UserCreate):
    id: int


"""Database configuration and access helpers."""

import sqlite3
from contextlib import contextmanager
from typing import Iterator

from project.config import settings
from project.errors import AppError
from project.models import SearchUserMatch, UserCreate, UserRecord


USER_TABLE_SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL
);
""".strip()


class Database:

    def __init__(self, database_path: str | None = None) -> None:
        self.database_path = database_path or str(settings.database_path)

    def connect(self) -> sqlite3.Connection:
        """Open a SQLite connection for the configured database path."""
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def initialize(self) -> None:
        with self.session() as connection:
            connection.execute(USER_TABLE_SCHEMA)
            connection.commit()

    def create_user(self, payload: UserCreate) -> UserRecord:
        try:
            with self.session() as connection:
                cursor = connection.execute(
                    """
                    INSERT INTO users (name, email, description)
                    VALUES (?, ?, ?)
                    """.strip(),
                    (payload.name, payload.email, payload.description),
                )
                connection.commit()
                user_id = int(cursor.lastrowid)
        except sqlite3.IntegrityError as exc:
            raise AppError("validation_error", "A user with this email already exists.") from exc
        except sqlite3.Error as exc:
            raise AppError("storage_error", "Failed to persist the user in SQLite.") from exc

        user = self.get_user_by_id(user_id)
        if user is None:
            raise AppError("storage_error", "Created user could not be read back from storage.")
        return user

    def get_user_by_id(self, user_id: int) -> UserRecord | None:
        with self.session() as connection:
            row = connection.execute(
                """
                SELECT id, name, email, description
                FROM users
                WHERE id = ?
                """.strip(),
                (user_id,),
            ).fetchone()

        if row is None:
            return None

        return UserRecord.from_row(dict(row))

    def get_users_by_ids(self, user_ids: list[int]) -> list[UserRecord]:
        if not user_ids:
            return []

        placeholders = ", ".join("?" for _ in user_ids)
        with self.session() as connection:
            rows = connection.execute(
                f"""
                SELECT id, name, email, description
                FROM users
                WHERE id IN ({placeholders})
                """.strip(),
                tuple(user_ids),
            ).fetchall()

        row_map = {int(row["id"]): UserRecord.from_row(dict(row)) for row in rows}
        return [row_map[user_id] for user_id in user_ids if user_id in row_map]

    def list_users(self) -> list[UserRecord]:
        with self.session() as connection:
            rows = connection.execute(
                """
                SELECT id, name, email, description
                FROM users
                ORDER BY id ASC
                """.strip()
            ).fetchall()

        return [UserRecord.from_row(dict(row)) for row in rows]

    def hydrate_search_matches(self, user_ids: list[int], scores: list[float]) -> list[SearchUserMatch]:
        users = self.get_users_by_ids(user_ids)
        user_map = {user.id: user for user in users}

        matches: list[SearchUserMatch] = []
        for user_id, score in zip(user_ids, scores):
            user = user_map.get(user_id)
            if user is None:
                continue
            matches.append(
                SearchUserMatch(
                    id=user.id,
                    name=user.name,
                    email=user.email,
                    description=user.description,
                    score=score,
                )
            )

        return matches

    @contextmanager
    def session(self) -> Iterator[sqlite3.Connection]:
        connection = self.connect()
        try:
            yield connection
        finally:
            connection.close()


def get_database() -> Database:
    return Database()

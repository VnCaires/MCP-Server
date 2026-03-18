"""Database configuration and access helpers."""

import sqlite3
from contextlib import contextmanager
from typing import Iterator

from project.config import settings
from project.models import UserCreate, UserRecord


USER_TABLE_SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL
);
""".strip()


class Database:
    """Thin wrapper around the project SQLite database."""

    def __init__(self, database_path: str | None = None) -> None:
        self.database_path = database_path or str(settings.database_path)

    def connect(self) -> sqlite3.Connection:
        """Open a SQLite connection for the configured database path."""
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def initialize(self) -> None:
        """Create the database schema required by the application."""
        with self.session() as connection:
            connection.execute(USER_TABLE_SCHEMA)
            connection.commit()

    def create_user(self, payload: UserCreate) -> UserRecord:
        """Persist a user and return the stored record."""
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
            raise ValueError("A user with this email already exists.") from exc

        user = self.get_user_by_id(user_id)
        if user is None:
            raise RuntimeError("Created user could not be read back from storage.")
        return user

    def get_user_by_id(self, user_id: int) -> UserRecord | None:
        """Return a stored user by ID or `None` if it does not exist."""
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

    @contextmanager
    def session(self) -> Iterator[sqlite3.Connection]:
        """Yield a connection and ensure it is always closed."""
        connection = self.connect()
        try:
            yield connection
        finally:
            connection.close()


def get_database() -> Database:
    """Build the default database dependency for the application."""
    return Database()

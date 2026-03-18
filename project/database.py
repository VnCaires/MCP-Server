"""Database configuration and access helpers."""

import sqlite3
from contextlib import contextmanager
from typing import Iterator

from project.config import settings


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

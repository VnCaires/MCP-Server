"""Database configuration and access helpers."""

import sqlite3
from contextlib import contextmanager
from typing import Iterator

from project.config import settings


class Database:
    """Thin wrapper around the project SQLite database."""

    def __init__(self, database_path: str | None = None) -> None:
        self.database_path = database_path or str(settings.database_path)

    def connect(self) -> sqlite3.Connection:
        """Open a SQLite connection for the configured database path."""
        return sqlite3.connect(self.database_path)

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


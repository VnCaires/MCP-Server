"""Database configuration and access helpers."""

from pathlib import Path
import sqlite3


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "crm.sqlite3"


def get_connection() -> sqlite3.Connection:
    """Return a SQLite connection for the project database."""
    return sqlite3.connect(DB_PATH)


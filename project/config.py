"""Centralized project configuration."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    """Filesystem settings shared across project modules."""

    base_dir: Path = Path(__file__).resolve().parent
    database_path: Path = base_dir / "crm.sqlite3"
    faiss_index_dir: Path = base_dir / "faiss_index"


settings = Settings()


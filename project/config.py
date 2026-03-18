"""Centralized project configuration."""

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    """Filesystem settings shared across project modules."""

    base_dir: Path = field(default_factory=lambda: Path(__file__).resolve().parent)
    embedding_dimensions: int = 128
    database_path: Path = field(init=False)
    faiss_index_dir: Path = field(init=False)
    faiss_metadata_path: Path = field(init=False)
    faiss_index_path: Path = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "database_path", self.base_dir / "crm.sqlite3")
        object.__setattr__(self, "faiss_index_dir", self.base_dir / "faiss_index")
        object.__setattr__(self, "faiss_metadata_path", self.faiss_index_dir / "metadata.json")
        object.__setattr__(self, "faiss_index_path", self.faiss_index_dir / "users.index")


settings = Settings()

"""FAISS index management primitives."""

from pathlib import Path

from project.config import settings


class VectorStore:
    """Handle the local storage concerns of the FAISS index."""

    def __init__(self, index_dir: Path | None = None) -> None:
        self.index_dir = index_dir or settings.faiss_index_dir

    def ensure_storage(self) -> Path:
        """Guarantee the FAISS storage directory exists."""
        self.index_dir.mkdir(exist_ok=True)
        return self.index_dir


def get_vector_store() -> VectorStore:
    """Build the default vector store dependency."""
    return VectorStore()

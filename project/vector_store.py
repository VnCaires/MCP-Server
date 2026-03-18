"""FAISS index management primitives."""

from pathlib import Path


INDEX_DIR = Path(__file__).resolve().parent / "faiss_index"


def ensure_index_dir() -> Path:
    """Guarantee the FAISS storage directory exists."""
    INDEX_DIR.mkdir(exist_ok=True)
    return INDEX_DIR


"""FAISS index management primitives."""

import json
from pathlib import Path

from project.config import settings
from project.models import VectorIndexEntry


class VectorStore:
    """Handle the local storage concerns of the FAISS index."""

    def __init__(self, index_dir: Path | None = None) -> None:
        self.index_dir = index_dir or settings.faiss_index_dir
        self.metadata_path = settings.faiss_metadata_path

    def ensure_storage(self) -> Path:
        """Guarantee the FAISS storage directory exists."""
        self.index_dir.mkdir(exist_ok=True)
        if not self.metadata_path.exists():
            self.metadata_path.write_text("[]", encoding="utf-8")
        return self.index_dir

    def register_user_vector(self, user_id: int) -> VectorIndexEntry:
        """Reserve a vector ID and bind it to a persisted user ID."""
        entries = self.load_entries()
        vector_id = len(entries)
        entry = VectorIndexEntry(vector_id=vector_id, user_id=user_id)
        entries.append(entry)
        self._write_entries(entries)
        return entry

    def get_user_id_for_vector(self, vector_id: int) -> int | None:
        """Return the user ID associated with a FAISS vector ID."""
        entries = self.load_entries()
        for entry in entries:
            if entry.vector_id == vector_id:
                return entry.user_id
        return None

    def get_user_ids_for_vectors(self, vector_ids: list[int]) -> list[int]:
        """Return user IDs for the given vector IDs, preserving order."""
        entry_map = {entry.vector_id: entry.user_id for entry in self.load_entries()}
        return [entry_map[vector_id] for vector_id in vector_ids if vector_id in entry_map]

    def load_entries(self) -> list[VectorIndexEntry]:
        """Load the vector-to-user mapping metadata from disk."""
        self.ensure_storage()
        raw_entries = json.loads(self.metadata_path.read_text(encoding="utf-8"))
        return [VectorIndexEntry.model_validate(entry) for entry in raw_entries]

    def _write_entries(self, entries: list[VectorIndexEntry]) -> None:
        """Persist vector mapping metadata to disk."""
        payload = [entry.model_dump() for entry in entries]
        self.metadata_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def get_vector_store() -> VectorStore:
    """Build the default vector store dependency."""
    return VectorStore()

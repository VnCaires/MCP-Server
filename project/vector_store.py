"""FAISS index management primitives."""

import json
from pathlib import Path

import faiss
import numpy as np

from project.config import settings
from project.models import VectorIndexEntry


class VectorStore:
    """Handle the local storage concerns of the FAISS index."""

    def __init__(self, index_dir: Path | None = None) -> None:
        self.index_dir = index_dir or settings.faiss_index_dir
        self.metadata_path = self.index_dir / "metadata.json"
        self.index_path = self.index_dir / "users.index"
        self.dimensions = settings.embedding_dimensions

    def ensure_storage(self) -> Path:
        """Guarantee the FAISS storage directory exists."""
        self.index_dir.mkdir(exist_ok=True)
        if not self.metadata_path.exists():
            self.metadata_path.write_text("[]", encoding="utf-8")
        if not self.index_path.exists():
            self._save_index(self._create_index())
            self._write_entries([])
        self._synchronize_metadata_with_index()
        return self.index_dir

    def add_vector(self, user_id: int, embedding: list[float]) -> VectorIndexEntry:
        """Add an embedding to the FAISS index and persist its user mapping."""
        vector = self._to_faiss_array(embedding)
        index = self.load_index()
        index.add(vector)
        vector_id = index.ntotal - 1
        self._save_index(index)
        return self.register_user_vector(user_id, vector_id)

    def search(self, embedding: list[float], top_k: int) -> tuple[list[int], list[float]]:
        """Search the FAISS index and return vector IDs with similarity scores."""
        index = self.load_index()
        if index.ntotal == 0:
            return [], []

        query = self._to_faiss_array(embedding)
        limit = min(top_k, index.ntotal)
        scores, vector_ids = index.search(query, limit)

        filtered_ids: list[int] = []
        filtered_scores: list[float] = []
        for vector_id, score in zip(vector_ids[0].tolist(), scores[0].tolist()):
            if vector_id < 0:
                continue
            filtered_ids.append(int(vector_id))
            filtered_scores.append(float(score))

        return filtered_ids, filtered_scores

    def register_user_vector(self, user_id: int, vector_id: int | None = None) -> VectorIndexEntry:
        """Reserve a vector ID and bind it to a persisted user ID."""
        entries = self.load_entries()
        next_vector_id = len(entries) if vector_id is None else vector_id
        entry = VectorIndexEntry(vector_id=next_vector_id, user_id=user_id)
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

    def load_index(self) -> faiss.IndexFlatIP:
        """Load the FAISS index from disk."""
        self.ensure_storage()
        return faiss.read_index(str(self.index_path))

    def _write_entries(self, entries: list[VectorIndexEntry]) -> None:
        """Persist vector mapping metadata to disk."""
        payload = [entry.model_dump() for entry in entries]
        self.metadata_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def _create_index(self) -> faiss.IndexFlatIP:
        """Build a fresh FAISS index for normalized embeddings."""
        return faiss.IndexFlatIP(self.dimensions)

    def _save_index(self, index: faiss.IndexFlatIP) -> None:
        """Persist the FAISS index to disk."""
        faiss.write_index(index, str(self.index_path))

    def _to_faiss_array(self, embedding: list[float]) -> np.ndarray:
        """Convert a Python list embedding into a FAISS-compatible array."""
        array = np.asarray([embedding], dtype=np.float32)
        if array.shape[1] != self.dimensions:
            raise ValueError(
                f"Embedding dimension mismatch: expected {self.dimensions}, got {array.shape[1]}."
            )
        return array

    def _synchronize_metadata_with_index(self) -> None:
        """Keep vector metadata aligned with the persisted FAISS index size."""
        if not self.index_path.exists() or not self.metadata_path.exists():
            return

        index = faiss.read_index(str(self.index_path))
        raw_entries = json.loads(self.metadata_path.read_text(encoding="utf-8"))
        entries = [VectorIndexEntry.model_validate(entry) for entry in raw_entries]
        expected_size = index.ntotal

        if len(entries) == expected_size:
            return

        normalized_entries = entries[:expected_size]
        self._write_entries(normalized_entries)


def get_vector_store() -> VectorStore:
    """Build the default vector store dependency."""
    return VectorStore()

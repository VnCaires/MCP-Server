"""Embedding provider abstractions."""

from hashlib import blake2b
from typing import Protocol
import re

import numpy as np

from project.config import settings


TOKEN_PATTERN = re.compile(r"\b\w+\b", re.UNICODE)


class EmbeddingProvider(Protocol):
    """Contract for text embedding backends."""

    def embed_text(self, text: str) -> list[float]:
        """Convert a piece of text into an embedding vector."""


class EmbeddingService:
    """Deterministic local embedding service for project development."""

    def __init__(self, dimensions: int | None = None) -> None:
        self.dimensions = dimensions or settings.embedding_dimensions

    def embed_description(self, description: str) -> list[float]:
        """Generate an embedding vector for a stored user description."""
        return self.embed_text(description)

    def embed_query(self, query: str) -> list[float]:
        """Generate an embedding vector for a semantic search query."""
        return self.embed_text(query)

    def embed_text(self, text: str) -> list[float]:
        """Convert text into a normalized deterministic vector."""
        normalized_text = text.strip().lower()
        if not normalized_text:
            raise ValueError("Text for embedding must not be empty.")

        vector = np.zeros(self.dimensions, dtype=np.float32)
        tokens = TOKEN_PATTERN.findall(normalized_text) or [normalized_text]

        for token in tokens:
            token_vector = self._token_to_vector(token)
            vector += token_vector

        norm = np.linalg.norm(vector)
        if norm == 0:
            raise ValueError("Text could not be converted into a valid embedding.")

        normalized_vector = vector / norm
        return normalized_vector.astype(np.float32).tolist()

    def _token_to_vector(self, token: str) -> np.ndarray:
        """Project a token into a stable dense vector space."""
        vector = np.zeros(self.dimensions, dtype=np.float32)
        digest_size = 32
        offset = 0
        seed = 0

        while offset < self.dimensions:
            digest = blake2b(f"{token}:{seed}".encode("utf-8"), digest_size=digest_size).digest()
            for byte in digest:
                if offset >= self.dimensions:
                    break
                vector[offset] = (byte / 255.0) * 2.0 - 1.0
                offset += 1
            seed += 1

        if not np.any(vector):
            vector[0] = 1.0

        return vector


def get_embedding_service() -> EmbeddingService:
    """Build the default embedding service dependency."""
    return EmbeddingService()

"""Embedding provider abstractions."""

from typing import Protocol


class EmbeddingProvider(Protocol):
    """Contract for text embedding backends."""

    def embed_text(self, text: str) -> list[float]:
        """Convert a piece of text into an embedding vector."""


class EmbeddingService:
    """Placeholder service for future embedding generation."""

    def embed_text(self, text: str) -> list[float]:
        raise NotImplementedError("Embedding generation will be implemented in a later issue.")


def get_embedding_service() -> EmbeddingService:
    """Build the default embedding service dependency."""
    return EmbeddingService()


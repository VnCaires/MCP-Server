"""Embedding provider abstractions."""


class EmbeddingService:
    """Placeholder service for future embedding generation."""

    def embed_text(self, text: str) -> list[float]:
        raise NotImplementedError("Embedding generation will be implemented in a later issue.")


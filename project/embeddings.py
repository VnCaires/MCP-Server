"""Embedding provider abstractions."""

from collections import Counter
from hashlib import blake2b
from typing import Protocol
import re
import unicodedata

import numpy as np

from project.config import settings


TOKEN_PATTERN = re.compile(r"\b\w+\b", re.UNICODE)
STOPWORDS = {
    "a",
    "ao",
    "aos",
    "as",
    "com",
    "como",
    "da",
    "das",
    "de",
    "do",
    "dos",
    "e",
    "em",
    "na",
    "nas",
    "no",
    "nos",
    "o",
    "os",
    "para",
    "por",
    "sem",
    "um",
    "uma",
    "usuario",
    "usuarios",
    "cliente",
    "clientes",
}


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
        normalized_text = self._normalize_text(text)
        if not normalized_text:
            raise ValueError("Text for embedding must not be empty.")

        vector = np.zeros(self.dimensions, dtype=np.float32)
        weighted_terms = self._extract_weighted_terms(normalized_text)
        if not weighted_terms:
            raise ValueError("Text could not be converted into a valid embedding.")

        for term, weight in weighted_terms.items():
            token_vector = self._token_to_vector(term)
            vector += token_vector * weight

        norm = np.linalg.norm(vector)
        if norm == 0:
            raise ValueError("Text could not be converted into a valid embedding.")

        normalized_vector = vector / norm
        return normalized_vector.astype(np.float32).tolist()

    def _normalize_text(self, text: str) -> str:
        """Lowercase and strip accents to compare related terms more consistently."""
        lowered = text.strip().lower()
        if not lowered:
            return ""

        normalized = unicodedata.normalize("NFKD", lowered)
        return "".join(char for char in normalized if not unicodedata.combining(char))

    def _extract_weighted_terms(self, normalized_text: str) -> Counter[str]:
        """Generate weighted lexical features while downranking generic CRM words."""
        raw_tokens = TOKEN_PATTERN.findall(normalized_text)
        tokens = [
            token
            for token in raw_tokens
            if token not in STOPWORDS and not token.isdigit() and len(token) >= 3
        ]
        if not tokens and raw_tokens:
            tokens = [token for token in raw_tokens if not token.isdigit()]

        weighted_terms: Counter[str] = Counter(tokens)
        for token in tokens:
            for ngram in self._token_ngrams(token):
                weighted_terms[ngram] += 0.35
        return weighted_terms

    def _token_ngrams(self, token: str) -> list[str]:
        """Add character n-grams so related word forms still land near each other."""
        if len(token) < 4:
            return []

        ngrams: list[str] = []
        for size in (3, 4):
            if len(token) < size:
                continue
            for index in range(len(token) - size + 1):
                ngrams.append(f"{size}g:{token[index:index + size]}")
        return ngrams

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

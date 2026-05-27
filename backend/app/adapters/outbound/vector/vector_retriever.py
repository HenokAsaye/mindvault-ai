"""Vector retriever adapter implementation."""

from __future__ import annotations

from typing import Any

from app.domain.ports.outbound.embedding_provider import EmbeddingProvider
from app.domain.ports.outbound.vector_store import VectorStore
from app.domain.value_objects.document import Document


class VectorRetriever:
    """Retriever using vector embeddings and ANN search."""

    def __init__(
        self,
        *,
        embedder: EmbeddingProvider,
        vector_store: VectorStore,
    ) -> None:
        self._embedder = embedder
        self._vector_store = vector_store

    async def retrieve(
        self,
        query: str,
        top_k: int = 5,
        filters: dict[str, Any] | None = None,
    ) -> list[Document]:
        if not query or not query.strip():
            raise ValueError("query must be a non-empty string")

        org_id = (filters or {}).get("org_id")
        if not org_id:
            raise ValueError("filters.org_id is required for vector retrieval")

        query_vector = await self._embedder.embed_text(query)
        matches = await self._vector_store.query_by_similarity(
            query_vector=query_vector,
            org_id=str(org_id),
            top_k=top_k,
        )

        results: list[Document] = []
        for match in matches:
            metadata = match.get("metadata") or {}
            text = (metadata.get("text") or "").strip()
            score = match.get("score")
            doc_id = match.get("id")
            if not doc_id or not text or score is None:
                continue
            if score < 0.0:
                score = 0.0
            elif score > 1.0:
                score = 1.0
            results.append(
                Document(
                    id=doc_id,
                    text=text,
                    score=score,
                    source="vector",
                    metadata=metadata,
                    vector_score=score,
                    retrieval_sources=["vector"],
                )
            )

        return results

"""Unit tests for HybridSearchService."""

from __future__ import annotations

import pytest

from app.application.services.hybrid_search_service import HybridSearchService
from app.domain.value_objects.document import Document

class FakeEmbedder:
    async def embed_text(self, text: str) -> list[float]:
        return [0.1, 0.2]

class FakeVectorStore:
    def __init__(self, results: list[dict]):
        self._results = results

    async def query_by_similarity(self, **kwargs) -> list[dict]:
        return self._results

class FakeFTS:
    def __init__(self, results: list[Document]):
        self._results = results

    async def search(self, **kwargs) -> list[Document]:
        return self._results

@pytest.mark.unit
@pytest.mark.asyncio
async def test_hybrid_search_skips_invalid_vector_matches() -> None:
    vector_store = FakeVectorStore(
        [
            {
                "id": "v1",
                "score": 0.9,
                "metadata": {"text": "alpha"},
            },
            {
                "id": "missing-text",
                "score": 0.5,
                "metadata": {},
            },
            {
                "id": "missing-score",
                "metadata": {"text": "beta"},
            },
        ]
    )
    fts = FakeFTS(
        [
            Document(
                id="k1",
                text="gamma",
                score=0.4,
                source="key",
                metadata={},
            )
        ]
    )

    service = HybridSearchService(
        embedder=FakeEmbedder(),
        vector_store=vector_store,
        full_text_search=fts,
    )

    results = await service.search(
        user_query="alpha",
        org_id="org-1",
        top_k=5,
    )

    ids = {doc.id for doc in results}
    assert ids == {"v1", "k1"}

@pytest.mark.unit
@pytest.mark.asyncio
async def test_hybrid_search_clamps_vector_score() -> None:
    vector_store = FakeVectorStore(
        [
            {
                "id": "v1",
                "score": 1.7,
                "metadata": {"text": "alpha"},
            }
        ]
    )
    fts = FakeFTS([])

    service = HybridSearchService(
        embedder=FakeEmbedder(),
        vector_store=vector_store,
        full_text_search=fts,
    )

    results = await service.search(
        user_query="alpha",
        org_id="org-1",
        top_k=5,
        use_rrf=False,
    )

    assert len(results) == 1
    assert 0.0 <= results[0].score <= 1.0

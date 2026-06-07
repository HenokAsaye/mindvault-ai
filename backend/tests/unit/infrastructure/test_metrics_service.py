"""Unit tests for metrics service."""

from __future__ import annotations

import pytest

from app.domain.entities.document import DocumentStatus
from app.infrastructure.observability.metrics import MetricsService
from tests.helpers.mocks import FakeChunkRepo, FakeDocumentRepo, make_document


@pytest.mark.unit
class TestMetricsService:
    async def test_counts_documents_and_chunks(self) -> None:
        org_id = make_document().org_id
        doc_repo = FakeDocumentRepo()
        doc = make_document(org_id=org_id, status=DocumentStatus.READY)
        doc_repo.documents[doc.id] = doc
        chunk_repo = FakeChunkRepo()
        chunk_repo.chunks = [type("C", (), {"org_id": org_id, "document_id": doc.id})()]

        metrics = MetricsService(
            documents=doc_repo, chunks=chunk_repo, org_id=str(org_id)
        )
        assert await metrics.get_total_documents() == 1
        assert await metrics.get_total_chunks() == 1
        assert await metrics.get_average_chunks_per_document() == 1.0

    async def test_average_chunks_zero_when_no_documents(self) -> None:
        metrics = MetricsService(
            documents=FakeDocumentRepo(),
            chunks=FakeChunkRepo(),
            org_id=str(make_document().org_id),
        )
        assert await metrics.get_average_chunks_per_document() == 0.0

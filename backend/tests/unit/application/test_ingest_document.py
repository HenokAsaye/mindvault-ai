"""Unit tests for document ingestion use case."""

from __future__ import annotations

from uuid import uuid4

import pytest

from app.application.use_cases.ingest_document import IngestDocumentService
from app.domain.entities.document import DocumentStatus
from app.domain.exceptions import (
    DocumentEmptyError,
    DocumentTooLargeError,
    UnsupportedSourceTypeError,
)
from app.domain.ports.inbound.ingestion_use_case import IngestDocumentCommand
from tests.helpers.mocks import FakeDocumentRepo, FakeMemoryStorage, make_document


@pytest.mark.unit
@pytest.mark.asyncio
async def test_ingest_stores_and_enqueues() -> None:
    org_id = uuid4()
    repo = FakeDocumentRepo()
    storage = FakeMemoryStorage()
    enqueued: list[str] = []

    service = IngestDocumentService(
        document_repository=repo,
        object_storage=storage,
        enqueue_processing=lambda document_id: enqueued.append(document_id),
        max_size_bytes=1_000_000,
        allowed_source_types={"text", "pdf"},
    )
    doc = await service.execute(
        IngestDocumentCommand(
            org_id=org_id,
            uploaded_by_user_id=uuid4(),
            title="notes.txt",
            source_type="text",
            content_type="text/plain",
            data=b"hello world",
        )
    )
    assert doc.status == DocumentStatus.PENDING
    assert doc.id in repo.documents
    assert enqueued == [str(doc.id)]
    assert storage.get_object(key=doc.storage_url) == b"hello world"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_ingest_returns_existing_on_duplicate_checksum() -> None:
    import hashlib

    org_id = uuid4()
    data = b"same content"
    checksum = hashlib.sha256(data).hexdigest()
    existing = make_document(org_id=org_id)
    existing.checksum = checksum
    repo = FakeDocumentRepo()
    repo.documents[existing.id] = existing
    repo.by_checksum[(org_id, checksum)] = existing

    service = IngestDocumentService(
        document_repository=repo,
        object_storage=FakeMemoryStorage(),
        enqueue_processing=lambda _: None,
        max_size_bytes=1_000_000,
        allowed_source_types={"text"},
    )
    result = await service.execute(
        IngestDocumentCommand(
            org_id=org_id,
            uploaded_by_user_id=None,
            title="dup",
            source_type="text",
            content_type=None,
            data=data,
        )
    )
    assert result.id == existing.id


@pytest.mark.unit
@pytest.mark.asyncio
async def test_ingest_rejects_empty_file() -> None:
    service = IngestDocumentService(
        document_repository=FakeDocumentRepo(),
        object_storage=FakeMemoryStorage(),
        enqueue_processing=lambda _: None,
        max_size_bytes=100,
        allowed_source_types={"text"},
    )
    with pytest.raises(DocumentEmptyError):
        await service.execute(
            IngestDocumentCommand(
                org_id=uuid4(),
                uploaded_by_user_id=None,
                title="x",
                source_type="text",
                content_type=None,
                data=b"",
            )
        )


@pytest.mark.unit
@pytest.mark.asyncio
async def test_ingest_rejects_oversized_file() -> None:
    service = IngestDocumentService(
        document_repository=FakeDocumentRepo(),
        object_storage=FakeMemoryStorage(),
        enqueue_processing=lambda _: None,
        max_size_bytes=10,
        allowed_source_types={"text"},
    )
    with pytest.raises(DocumentTooLargeError):
        await service.execute(
            IngestDocumentCommand(
                org_id=uuid4(),
                uploaded_by_user_id=None,
                title="x",
                source_type="text",
                content_type=None,
                data=b"x" * 20,
            )
        )


@pytest.mark.unit
@pytest.mark.asyncio
async def test_ingest_rejects_unsupported_type() -> None:
    service = IngestDocumentService(
        document_repository=FakeDocumentRepo(),
        object_storage=FakeMemoryStorage(),
        enqueue_processing=lambda _: None,
        max_size_bytes=1000,
        allowed_source_types={"text"},
    )
    with pytest.raises(UnsupportedSourceTypeError):
        await service.execute(
            IngestDocumentCommand(
                org_id=uuid4(),
                uploaded_by_user_id=None,
                title="x",
                source_type="video/mp4",
                content_type=None,
                data=b"data",
            )
        )


@pytest.mark.unit
@pytest.mark.asyncio
async def test_ingest_marks_failed_when_enqueue_raises() -> None:
    org_id = uuid4()
    repo = FakeDocumentRepo()

    def _boom(document_id: str) -> None:
        raise RuntimeError("broker down")

    service = IngestDocumentService(
        document_repository=repo,
        object_storage=FakeMemoryStorage(),
        enqueue_processing=_boom,
        max_size_bytes=1_000_000,
        allowed_source_types={"text"},
    )
    doc = await service.execute(
        IngestDocumentCommand(
            org_id=org_id,
            uploaded_by_user_id=None,
            title="f.txt",
            source_type="text",
            content_type=None,
            data=b"content",
        )
    )
    assert doc.status == DocumentStatus.FAILED

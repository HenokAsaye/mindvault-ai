"""Unit tests for synchronous document chunk processing."""

from __future__ import annotations

from uuid import uuid4

import pytest

from app.adapters.outbound.loaders.text_loader import TextDocumentLoader
from app.application.use_cases.process_document_chunks import (
    ProcessDocumentChunksService,
)
from app.domain.entities.document import DocumentStatus
from app.domain.ports.outbound.document_loader import DocumentLoaderRegistry
from app.domain.services.chunking_policy import ChunkingConfig
from tests.helpers.mocks import (
    FakeEmbedder,
    FakeMemoryStorage,
    FakeSyncChunkRepo,
    FakeSyncDocumentRepo,
    FakeVectorStore,
    make_document,
)

@pytest.mark.unit
def test_process_document_chunks_full_pipeline() -> None:
    doc = make_document(status=DocumentStatus.PENDING, storage_key="k1")
    storage = FakeMemoryStorage()
    storage.put_object(key="k1", data=b"Alpha.\n\nBeta paragraph here.")
    doc_repo = FakeSyncDocumentRepo(documents={doc.id: doc})
    chunk_repo = FakeSyncChunkRepo()
    vector = FakeVectorStore()

    service = ProcessDocumentChunksService(
        document_repository=doc_repo,
        chunk_repository=chunk_repo,
        object_storage=storage,
        loader_registry=DocumentLoaderRegistry([TextDocumentLoader()]),
        chunking_config=ChunkingConfig(chunk_size_chars=50, chunk_overlap_chars=10),
        embedding_provider=FakeEmbedder(),
        vector_store=vector,
    )
    count = service.execute(document_id=doc.id)
    assert count >= 1
    assert doc.status == DocumentStatus.READY
    assert len(chunk_repo.chunks) == count
    assert len(vector.upserted) == 1

@pytest.mark.unit
def test_process_skips_missing_document() -> None:
    service = ProcessDocumentChunksService(
        document_repository=FakeSyncDocumentRepo(),
        chunk_repository=FakeSyncChunkRepo(),
        object_storage=FakeMemoryStorage(),
        loader_registry=DocumentLoaderRegistry([TextDocumentLoader()]),
        chunking_config=ChunkingConfig(),
        embedding_provider=FakeEmbedder(),
        vector_store=FakeVectorStore(),
    )
    assert service.execute(document_id=uuid4()) == 0

@pytest.mark.unit
def test_process_skips_already_ready() -> None:
    doc = make_document(status=DocumentStatus.READY)
    doc.chunk_count = 3
    service = ProcessDocumentChunksService(
        document_repository=FakeSyncDocumentRepo(documents={doc.id: doc}),
        chunk_repository=FakeSyncChunkRepo(),
        object_storage=FakeMemoryStorage(),
        loader_registry=DocumentLoaderRegistry([TextDocumentLoader()]),
        chunking_config=ChunkingConfig(),
        embedding_provider=FakeEmbedder(),
        vector_store=FakeVectorStore(),
    )
    assert service.execute(document_id=doc.id) == 3

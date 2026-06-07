"""Integration tests for document API routes."""

from __future__ import annotations

from uuid import uuid4

import pytest

from app.application.use_cases.ingest_document import IngestDocumentService
from tests.helpers.mocks import (
    FakeChunkRepo,
    FakeDocumentRepo,
    FakeMemoryStorage,
    make_document,
)

ROUTES = "app.adapters.inbound.api.v1.routes_documents"

@pytest.mark.integration
def test_upload_document_accepted(authed_client, test_org_id, monkeypatch) -> None:
    doc = make_document(org_id=test_org_id)

    class FakeIngest:
        async def execute(self, command):
            return doc

    monkeypatch.setattr(f"{ROUTES}.get_ingest_document_service", lambda: FakeIngest())
    files = {"file": ("notes.txt", b"hello", "text/plain")}
    response = authed_client.post(
        "/api/v1/documents",
        files=files,
        headers={"Authorization": "Bearer x"},
    )
    assert response.status_code == 202
    assert response.json()["id"] == str(doc.id)

@pytest.mark.integration
def test_upload_empty_file_400(authed_client, monkeypatch) -> None:
    service = IngestDocumentService(
        document_repository=FakeDocumentRepo(),
        object_storage=FakeMemoryStorage(),
        enqueue_processing=lambda _: None,
        max_size_bytes=1_000_000,
        allowed_source_types={"text"},
    )
    monkeypatch.setattr(f"{ROUTES}.get_ingest_document_service", lambda: service)
    response = authed_client.post(
        "/api/v1/documents",
        files={"file": ("empty.txt", b"", "text/plain")},
        headers={"Authorization": "Bearer x"},
    )
    assert response.status_code == 400

@pytest.mark.integration
def test_list_documents(authed_client, test_org_id, monkeypatch) -> None:
    doc = make_document(org_id=test_org_id)
    repo = FakeDocumentRepo(documents={doc.id: doc})
    monkeypatch.setattr(f"{ROUTES}.get_document_repository", lambda: repo)
    response = authed_client.get(
        "/api/v1/documents",
        headers={"Authorization": "Bearer x"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["id"] == str(doc.id)

@pytest.mark.integration
def test_get_document_not_found(authed_client, monkeypatch) -> None:
    monkeypatch.setattr(f"{ROUTES}.get_document_repository", lambda: FakeDocumentRepo())
    response = authed_client.get(
        f"/api/v1/documents/{uuid4()}",
        headers={"Authorization": "Bearer x"},
    )
    assert response.status_code == 404

@pytest.mark.integration
def test_list_chunks(authed_client, test_org_id, monkeypatch) -> None:
    doc = make_document(org_id=test_org_id)
    doc_repo = FakeDocumentRepo(documents={doc.id: doc})
    chunk_repo = FakeChunkRepo()

    class Chunk:
        def __init__(self):
            self.id = uuid4()
            self.document_id = doc.id
            self.chunk_index = 0
            self.content = "chunk text"
            self.content_hash = "hash"

    chunk_repo.chunks = [Chunk()]
    monkeypatch.setattr(f"{ROUTES}.get_document_repository", lambda: doc_repo)
    monkeypatch.setattr(f"{ROUTES}.get_chunk_repository", lambda: chunk_repo)
    response = authed_client.get(
        f"/api/v1/documents/{doc.id}/chunks",
        headers={"Authorization": "Bearer x"},
    )
    assert response.status_code == 200
    assert response.json()["total"] == 1

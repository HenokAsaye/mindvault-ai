from __future__ import annotations

from app.domain.ports.outbound.document_repository import DocumentRepository
from app.domain.ports.outbound.chunk_repository import ChunkRepository
from app.infrastructure.di.providers import (
    get_document_repository,
    get_chunk_repository,
)


class MetricsService:
    def __init__(
        self,
        *,
        documents: DocumentRepository | None = None,
        chunks: ChunkRepository | None = None,
        org_id: str = "",
    ) -> None:
        self._documents = documents or get_document_repository()
        self._chunks = chunks or get_chunk_repository()
        self._org_id = org_id

    async def get_total_documents(self) -> int:
        return await self._documents.count_by_org(self._org_id)

    async def get_total_chunks(self) -> int:
        return await self._chunks.count_by_org(self._org_id)

    async def get_total_failed_documents(self) -> int:
        return await self._documents.count_failed_by_org(self._org_id)

    async def get_average_chunks_per_document(self) -> float:
        total_docs = await self.get_total_documents()
        if total_docs == 0:
            return 0.0
        total_chunks = await self.get_total_chunks()
        return total_chunks / total_docs

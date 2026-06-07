from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import delete, func, select, update

from app.adapters.outbound.db.celery_worker_db import worker_session
from app.adapters.outbound.db.sqlalchemy_models import DocumentChunkORM, DocumentORM
from app.domain.entities.document import Document, DocumentStatus
from app.domain.entities.document_chunk import DocumentChunk
from app.domain.ports.outbound.chunk_repository import (
    ChunkRepository,
    SyncChunkRepository,
)
from app.domain.ports.outbound.document_repository import (
    DocumentRepository,
    SyncDocumentRepository,
)


def _document_orm_to_entity(row: DocumentORM) -> Document:
    return Document(
        id=UUID(row.id) if isinstance(row.id, str) else row.id,
        org_id=UUID(row.org_id) if isinstance(row.org_id, str) else row.org_id,
        title=row.title,
        source_type=row.source_type,
        storage_url=row.storage_url,
        checksum=row.checksum,
        status=DocumentStatus(row.status),
        metadata=dict(row.metadata_json or {}),
        chunk_count=row.chunk_count,
        token_count=row.token_count,
        error_message=row.error_message,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


class DocumentRepositoryImpl(DocumentRepository):
    """Async repository used by API request handlers."""

    def __init__(self, *, session_factory) -> None:
        self._session_factory = session_factory

    async def save(self, document: Document) -> None:
        async with self._session_factory() as session:
            session.add(
                DocumentORM(
                    id=document.id,
                    org_id=document.org_id,
                    title=document.title,
                    source_type=document.source_type,
                    storage_url=document.storage_url,
                    checksum=document.checksum,
                    status=document.status.value,
                    metadata_json=document.metadata or {},
                    chunk_count=document.chunk_count,
                    token_count=document.token_count,
                    error_message=document.error_message,
                )
            )
            await session.commit()

    async def get_by_id(
        self, *, document_id: UUID, org_id: UUID | None = None
    ) -> Document | None:
        async with self._session_factory() as session:
            stmt = select(DocumentORM).where(DocumentORM.id == document_id)
            if org_id is not None:
                stmt = stmt.where(DocumentORM.org_id == org_id)
            row = (await session.execute(stmt)).scalar_one_or_none()
            return _document_orm_to_entity(row) if row else None

    async def delete(self, *, document_id: UUID, org_id: UUID) -> None:
        async with self._session_factory() as session:
            await session.execute(
                delete(DocumentORM).where(
                    DocumentORM.id == document_id,
                    DocumentORM.org_id == org_id,
                )
            )
            await session.commit()

    async def list_by_org_id(
        self,
        *,
        org_id: UUID,
        page: int = 1,
        page_size: int = 20,
        status: str | None = None,
    ) -> tuple[list[Document], int]:
        async with self._session_factory() as session:
            base_stmt = select(DocumentORM).where(DocumentORM.org_id == org_id)
            if status:
                base_stmt = base_stmt.where(DocumentORM.status == status)
            offset = max(0, (page - 1) * page_size)
            rows = (
                (
                    await session.execute(
                        base_stmt.order_by(DocumentORM.created_at.desc())
                        .offset(offset)
                        .limit(page_size)
                    )
                )
                .scalars()
                .all()
            )
            count_stmt = (
                select(func.count())
                .select_from(DocumentORM)
                .where(DocumentORM.org_id == org_id)
            )
            if status:
                count_stmt = count_stmt.where(DocumentORM.status == status)
            total = (await session.execute(count_stmt)).scalar_one()
        return [_document_orm_to_entity(r) for r in rows], int(total)

    async def find_by_checksum(self, *, org_id: UUID, checksum: str) -> Document | None:
        async with self._session_factory() as session:
            stmt = select(DocumentORM).where(
                DocumentORM.org_id == org_id,
                DocumentORM.checksum == checksum,
            )
            row = (await session.execute(stmt)).scalar_one_or_none()
            return _document_orm_to_entity(row) if row else None

    async def count_by_org(self, org_id: str) -> int:
        async with self._session_factory() as session:
            stmt = (
                select(func.count())
                .select_from(DocumentORM)
                .where(DocumentORM.org_id == org_id)
            )
            result = await session.execute(stmt)
            return result.scalar_one()

    async def count_failed_by_org(self, org_id: str) -> int:
        async with self._session_factory() as session:
            stmt = (
                select(func.count())
                .select_from(DocumentORM)
                .where(
                    DocumentORM.org_id == org_id,
                    DocumentORM.status == DocumentStatus.FAILED.value,
                )
            )
            result = await session.execute(stmt)
            return result.scalar_one()

    async def update_status(
        self,
        *,
        document_id: UUID,
        status: str,
        error_message: str | None = None,
        chunk_count: int | None = None,
        token_count: int | None = None,
    ) -> None:
        values: dict[str, object] = {
            "status": status,
            "updated_at": datetime.now(timezone.utc),
        }
        if error_message is not None:
            values["error_message"] = error_message
        if chunk_count is not None:
            values["chunk_count"] = chunk_count
        if token_count is not None:
            values["token_count"] = token_count
        async with self._session_factory() as session:
            await session.execute(
                update(DocumentORM)
                .where(DocumentORM.id == document_id)
                .values(**values)
            )
            await session.commit()


class SyncDocumentRepositoryImpl(SyncDocumentRepository):
    def get_by_id(self, *, document_id: UUID) -> Document | None:
        with worker_session() as session:
            row = session.execute(
                select(DocumentORM).where(DocumentORM.id == document_id)
            ).scalar_one_or_none()
            return _document_orm_to_entity(row) if row else None

    def update_status(
        self,
        *,
        document_id: UUID,
        status: str,
        error_message: str | None = None,
        chunk_count: int | None = None,
        token_count: int | None = None,
    ) -> None:
        values: dict[str, object] = {
            "status": status,
            "updated_at": datetime.now(timezone.utc),
        }
        if error_message is not None:
            values["error_message"] = error_message
        if chunk_count is not None:
            values["chunk_count"] = chunk_count
        if token_count is not None:
            values["token_count"] = token_count
        with worker_session() as session:
            session.execute(
                update(DocumentORM)
                .where(DocumentORM.id == document_id)
                .values(**values)
            )
            session.commit()


class SyncChunkRepositoryImpl(SyncChunkRepository):
    """Sync chunk repository used by Celery workers."""

    def add_many(self, chunks: list[DocumentChunk]) -> None:
        if not chunks:
            return
        with worker_session() as session:
            session.add_all(
                [
                    DocumentChunkORM(
                        id=c.id,
                        org_id=c.org_id,
                        document_id=c.document_id,
                        chunk_index=c.chunk_index,
                        content=c.content,
                        content_hash=c.content_hash,
                        embedding_id=c.embedding_id,
                        metadata_json=c.metadata or {},
                        citation_page_start=c.citation_page_start,
                        citation_page_end=c.citation_page_end,
                        citation_line_start=c.citation_line_start,
                        citation_line_end=c.citation_line_end,
                    )
                    for c in chunks
                ]
            )
            session.commit()

    def delete_by_document(self, *, document_id: UUID) -> None:
        with worker_session() as session:
            session.execute(
                delete(DocumentChunkORM).where(
                    DocumentChunkORM.document_id == document_id
                )
            )
            session.commit()


class ChunkRepositoryImpl(ChunkRepository):
    """Async chunk repository (used by API: list/delete)."""

    def __init__(self, *, session_factory) -> None:
        self._session_factory = session_factory

    async def add_many(self, chunks: list[DocumentChunk]) -> None:
        if not chunks:
            return
        async with self._session_factory() as session:
            session.add_all(
                [
                    DocumentChunkORM(
                        id=c.id,
                        org_id=c.org_id,
                        document_id=c.document_id,
                        chunk_index=c.chunk_index,
                        content=c.content,
                        content_hash=c.content_hash,
                        embedding_id=c.embedding_id,
                        metadata_json=c.metadata or {},
                        citation_page_start=c.citation_page_start,
                        citation_page_end=c.citation_page_end,
                        citation_line_start=c.citation_line_start,
                        citation_line_end=c.citation_line_end,
                    )
                    for c in chunks
                ]
            )
            await session.commit()

    async def list_by_document(self, *, document_id: UUID) -> list[DocumentChunk]:
        async with self._session_factory() as session:
            rows = (
                (
                    await session.execute(
                        select(DocumentChunkORM)
                        .where(DocumentChunkORM.document_id == document_id)
                        .order_by(DocumentChunkORM.chunk_index.asc())
                    )
                )
                .scalars()
                .all()
            )
        return [
            DocumentChunk(
                id=r.id,
                org_id=r.org_id,
                document_id=r.document_id,
                chunk_index=r.chunk_index,
                content=r.content,
                content_hash=r.content_hash,
                embedding_id=r.embedding_id,
                metadata=dict(r.metadata_json or {}),
                citation_page_start=r.citation_page_start,
                citation_page_end=r.citation_page_end,
                citation_line_start=r.citation_line_start,
                citation_line_end=r.citation_line_end,
                created_at=r.created_at,
            )
            for r in rows
        ]

    async def count_by_org(self, org_id: str) -> int:
        async with self._session_factory() as session:
            stmt = (
                select(func.count())
                .select_from(DocumentChunkORM)
                .where(DocumentChunkORM.org_id == org_id)
            )
            result = await session.execute(stmt)
            return result.scalar_one()

    async def delete_by_document(self, *, document_id: UUID) -> None:
        async with self._session_factory() as session:
            await session.execute(
                delete(DocumentChunkORM).where(
                    DocumentChunkORM.document_id == document_id
                )
            )
            await session.commit()

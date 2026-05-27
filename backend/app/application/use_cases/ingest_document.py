from __future__ import annotations

import asyncio
import hashlib
import logging
import re
from uuid import uuid4

from app.domain.entities.document import Document, DocumentStatus
from app.domain.exceptions import (
    DocumentEmptyError,
    DocumentTooLargeError,
    UnsupportedSourceTypeError,
)
from app.domain.ports.inbound.ingestion_use_case import (
    IngestDocumentCommand,
    IngestDocumentUseCase,
)
from app.domain.ports.outbound.document_repository import DocumentRepository
from app.domain.ports.outbound.object_storage import ObjectStorage

logger = logging.getLogger(__name__)


_FILENAME_SAFE = re.compile(r"[^A-Za-z0-9._-]+")


def _safe_filename(title: str, fallback: str = "document") -> str:
    base = _FILENAME_SAFE.sub("_", (title or "").strip()).strip("._-")
    return base or fallback


class IngestDocumentService(IngestDocumentUseCase):
    def __init__(
        self,
        *,
        document_repository: DocumentRepository,
        object_storage: ObjectStorage,
        enqueue_processing,
        max_size_bytes: int,
        allowed_source_types: set[str],
    ) -> None:
        self._documents = document_repository
        self._storage = object_storage
        self._enqueue_processing = enqueue_processing
        self._max_size_bytes = max_size_bytes
        self._allowed_source_types = {t.lower() for t in allowed_source_types}

    async def execute(self, command: IngestDocumentCommand) -> Document:
        if not command.data:
            raise DocumentEmptyError("Uploaded file is empty")
        if len(command.data) > self._max_size_bytes:
            raise DocumentTooLargeError(
                f"Uploaded file exceeds max size of {self._max_size_bytes} bytes"
            )
        normalized_type = (command.source_type or "").lower()
        if normalized_type not in self._allowed_source_types:
            raise UnsupportedSourceTypeError(
                f"Unsupported source_type={command.source_type!r}. "
                f"Allowed: {sorted(self._allowed_source_types)}"
            )

        new_document_id = uuid4()
        checksum = hashlib.sha256(command.data).hexdigest()
        storage_key = (
            f"{command.org_id}/{new_document_id}-{_safe_filename(command.title)}"
        )

        existing = await self._documents.find_by_checksum(
            org_id=command.org_id,
            checksum=checksum,
        )
        if existing is not None:
            logger.info(
                "Duplicate document upload detected for org_id=%s with checksum %s. "
                "Existing document_id=%s will be reused.",
                command.org_id,
                checksum,
                existing.id,
            )
            return existing
        await asyncio.to_thread(
            self._storage.put_object,
            key=storage_key,
            data=command.data,
            content_type=command.content_type,
        )

        document = Document(
            id=new_document_id,
            org_id=command.org_id,
            title=command.title.strip() or _safe_filename("document"),
            source_type=normalized_type,
            storage_url=storage_key,
            checksum=checksum,
            status=DocumentStatus.PENDING,
            metadata={
                "content_type": command.content_type or "",
                "uploaded_by": (
                    str(command.uploaded_by_user_id)
                    if command.uploaded_by_user_id
                    else None
                ),
                "size_bytes": len(command.data),
            },
        )
        await self._documents.save(document)

        try:
            self._enqueue_processing(document_id=str(new_document_id))
        except Exception:

            logger.exception(
                "Failed to enqueue processing for document %s", new_document_id
            )
            await self._documents.update_status(
                document_id=new_document_id,
                status=DocumentStatus.FAILED.value,
                error_message="Failed to enqueue processing job",
            )
            document.status = DocumentStatus.FAILED
            document.error_message = "Failed to enqueue processing job"

        return document

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID

from app.domain.entities.document import Document

@dataclass(slots=True, frozen=True)
class IngestDocumentCommand:
    org_id: UUID
    uploaded_by_user_id: UUID | None
    title: str
    source_type: str
    content_type: str | None
    data: bytes

class IngestDocumentUseCase(ABC):
    @abstractmethod
    async def execute(self, command: IngestDocumentCommand) -> Document:
        """Persist the upload and enqueue background processing."""

class ProcessDocumentChunksUseCase(ABC):
    @abstractmethod
    def execute(self, *, document_id: UUID) -> int:
        """Synchronously load + chunk a document. Returns chunk count."""

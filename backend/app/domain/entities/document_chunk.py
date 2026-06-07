from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import UUID


@dataclass(slots=True)
class DocumentChunk:

    id: UUID
    org_id: UUID
    document_id: UUID
    chunk_index: int
    content: str
    content_hash: str
    embedding_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    citation_page_start: int | None = None
    citation_page_end: int | None = None
    citation_line_start: int | None = None
    citation_line_end: int | None = None
    created_at: datetime | None = None

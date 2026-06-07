from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID


class DocumentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"


@dataclass(slots=True)
class Document:
    id: UUID
    org_id: UUID
    title: str
    source_type: str
    storage_url: str
    checksum: str | None = None
    status: DocumentStatus = DocumentStatus.PENDING
    metadata: dict[str, Any] = field(default_factory=dict)
    chunk_count: int = 0
    token_count: int = 0
    error_message: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import UUID


@dataclass(slots=True)
class ChatSession:
    id: UUID
    org_id: UUID
    user_id: UUID
    title: str
    metadata: dict[str, Any] = field(default_factory=dict)
    last_message_at: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

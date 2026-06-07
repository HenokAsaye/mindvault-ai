from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import UUID, uuid4


@dataclass(slots=True)
class ChatMessage:
    id: UUID
    session_id: UUID
    org_id: UUID
    user_id: UUID
    role: str
    content: str
    citations: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    model_id: str | None = None
    token_count: int | None = None
    created_at: datetime | None = None

    @classmethod
    def create_user_message(
        cls, session_id: UUID, org_id: UUID, user_id: UUID, content: str
    ) -> ChatMessage:
        return cls(
            id=uuid4(),
            session_id=session_id,
            org_id=org_id,
            user_id=user_id,
            role="user",
            content=content,
        )

    @classmethod
    def create_assistant_message(
        cls,
        session_id: UUID,
        org_id: UUID,
        user_id: UUID,
        content: str,
        citations: list[dict[str, Any]] | None = None,
        model_id: str | None = None,
        token_count: int | None = None,
    ) -> ChatMessage:
        return cls(
            id=uuid4(),
            session_id=session_id,
            org_id=org_id,
            user_id=user_id,
            role="assistant",
            content=content,
            citations=citations or [],
            model_id=model_id,
            token_count=token_count,
        )

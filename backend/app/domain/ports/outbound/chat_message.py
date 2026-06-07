from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.entities.chat_message import ChatMessage


class ChatMessageRepository(ABC):
    @abstractmethod
    async def add_message(self, chat_message: ChatMessage) -> None: ...

    @abstractmethod
    async def list_messages(self, session_id: UUID) -> list[ChatMessage]: ...

    @abstractmethod
    async def get_recent_by_session(
        self, session_id: UUID, limit: int = 10
    ) -> list[ChatMessage]: ...

    @abstractmethod
    async def delete_messages(self, session_id: UUID) -> None: ...

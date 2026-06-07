from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.entities.chat_session import ChatSession


class ChatSessionRepository(ABC):
    @abstractmethod
    async def create_chat_session(self, chat_session: ChatSession) -> None: ...

    @abstractmethod
    async def get_chat_session(self, session_id: UUID) -> ChatSession: ...

    @abstractmethod
    async def update_chat_session(self, chat_session: ChatSession) -> None: ...

    @abstractmethod
    async def delete_chat_session(self, session_id: UUID) -> None: ...

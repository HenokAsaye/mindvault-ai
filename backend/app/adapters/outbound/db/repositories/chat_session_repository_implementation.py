from __future__ import annotations

from uuid import UUID

from sqlalchemy import select, update, delete as sa_delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.chat_session import ChatSession
from app.domain.ports.outbound.chat_session import ChatSessionRepository
from app.adapters.outbound.db.sqlalchemy_models import ChatSessionORM


class NotFound(Exception):
    pass


class ChatSessionRepositoryImplementation(ChatSessionRepository):
    def __init__(self, db_session: AsyncSession) -> None:
        self.db_session = db_session

    async def create_chat_session(self, chat_session: ChatSession) -> None:
        orm = ChatSessionORM(
            id=chat_session.id,
            org_id=chat_session.org_id,
            user_id=chat_session.user_id,
            title=chat_session.title,
            metadata_json=chat_session.metadata,
            last_message_at=chat_session.last_message_at,
        )
        self.db_session.add(orm)

    async def get_chat_session(self, session_id: UUID) -> ChatSession:
        result = await self.db_session.execute(
            select(ChatSessionORM).where(ChatSessionORM.id == session_id)
        )
        orm = result.scalar_one_or_none()
        if orm is None:
            raise NotFound(f"ChatSession {session_id} not found")
        return ChatSession(
            id=orm.id,
            org_id=orm.org_id,
            user_id=orm.user_id,
            title=orm.title,
            metadata=orm.metadata_json or {},
            last_message_at=orm.last_message_at,
            created_at=orm.created_at,
            updated_at=orm.updated_at,
        )

    async def update_chat_session(self, chat_session: ChatSession) -> None:
        stmt = (
            update(ChatSessionORM)
            .where(ChatSessionORM.id == chat_session.id)
            .values(
                title=chat_session.title,
                metadata_json=chat_session.metadata,
                last_message_at=chat_session.last_message_at,
            )
        )
        await self.db_session.execute(stmt)

    async def delete_chat_session(self, session_id: UUID) -> None:
        stmt = sa_delete(ChatSessionORM).where(ChatSessionORM.id == session_id)
        await self.db_session.execute(stmt)

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select, delete as sa_delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.chat_message import ChatMessage
from app.domain.ports.outbound.chat_message import ChatMessageRepository
from app.adapters.outbound.db.sqlalchemy_models import ChatMessageORM


class NotFound(Exception):
    pass


class ChatMessageRepositoryImplementation(ChatMessageRepository):
    def __init__(self, db_session: AsyncSession) -> None:
        self.db_session = db_session

    async def add_message(self, chat_message: ChatMessage) -> None:
        orm = ChatMessageORM(
            id=chat_message.id,
            session_id=chat_message.session_id,
            org_id=chat_message.org_id,
            user_id=chat_message.user_id,
            role=chat_message.role,
            content=chat_message.content,
            citations=chat_message.citations,
            metadata_json=chat_message.metadata,
            model_id=chat_message.model_id,
            token_count=chat_message.token_count,
        )
        self.db_session.add(orm)

    async def list_messages(self, session_id: UUID) -> list[ChatMessage]:
        return await self._fetch_messages(session_id)

    async def get_recent_by_session(
        self, session_id: UUID, limit: int = 10
    ) -> list[ChatMessage]:
        result = await self.db_session.execute(
            select(ChatMessageORM)
            .where(ChatMessageORM.session_id == session_id)
            .order_by(ChatMessageORM.created_at.desc())
            .limit(limit)
        )
        orms = list(result.scalars().all())
        orms.reverse()
        return [self._to_domain(orm) for orm in orms]

    async def delete_messages(self, session_id: UUID) -> None:
        stmt = sa_delete(ChatMessageORM).where(ChatMessageORM.session_id == session_id)
        await self.db_session.execute(stmt)

    async def _fetch_messages(self, session_id: UUID) -> list[ChatMessage]:
        result = await self.db_session.execute(
            select(ChatMessageORM)
            .where(ChatMessageORM.session_id == session_id)
            .order_by(ChatMessageORM.created_at)
        )
        return [self._to_domain(orm) for orm in result.scalars().all()]

    @staticmethod
    def _to_domain(orm: ChatMessageORM) -> ChatMessage:
        return ChatMessage(
            id=orm.id,
            session_id=orm.session_id,
            org_id=orm.org_id,
            user_id=orm.user_id,
            role=orm.role,
            content=orm.content,
            citations=orm.citations or [],
            metadata=orm.metadata_json or {},
            model_id=orm.model_id,
            token_count=orm.token_count,
            created_at=orm.created_at,
        )

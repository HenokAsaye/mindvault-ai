from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.adapters.outbound.db.repositories import (
    chat_message_repository_implementation,
    chat_session_repository_implementation,
    membership_repository_impl,
    organization_repository_impl,
    user_repository_impl,
)
from app.domain.ports.outbound.unit_of_work import UnitOfWork


class SQLAlchemyUnitOfWork(UnitOfWork):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory
        self._session: AsyncSession | None = None
        self._committed = False
        self.users = None
        self.organizations = None
        self.memberships = None
        self.sessions = None
        self.messages = None

    async def __aenter__(self) -> "SQLAlchemyUnitOfWork":
        self._session = self._session_factory()
        self._committed = False
        self.users = user_repository_impl.UserRepositoryImpl(db=self._session)
        self.organizations = organization_repository_impl.OrganizationRepositoryImpl(
            db=self._session
        )
        self.memberships = membership_repository_impl.MembershipRepositoryImpl(
            db=self._session
        )
        self.sessions = (
            chat_session_repository_implementation.ChatSessionRepositoryImplementation(
                db_session=self._session
            )
        )
        self.messages = (
            chat_message_repository_implementation.ChatMessageRepositoryImplementation(
                db_session=self._session
            )
        )
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        if not self._session:
            return
        if exc or not self._committed:
            await self._session.rollback()
        await self._session.close()

    async def commit(self) -> None:
        if self._session:
            await self._session.commit()
            self._committed = True

    async def rollback(self) -> None:
        if self._session:
            await self._session.rollback()
            self._committed = False

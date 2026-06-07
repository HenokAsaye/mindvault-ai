from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.ports.outbound.chat_message import ChatMessageRepository
from app.domain.ports.outbound.chat_session import ChatSessionRepository
from app.domain.ports.outbound.membership_repository import MembershipRepository
from app.domain.ports.outbound.organization_repository import OrganizationRepository
from app.domain.ports.outbound.user_repository import UserRepository

class UnitOfWork(ABC):
    users: UserRepository
    organizations: OrganizationRepository
    memberships: MembershipRepository
    sessions: ChatSessionRepository
    messages: ChatMessageRepository

    @abstractmethod
    async def __aenter__(self) -> "UnitOfWork": ...

    @abstractmethod
    async def __aexit__(self, exc_type, exc, tb) -> None: ...

    @abstractmethod
    async def commit(self) -> None: ...

    @abstractmethod
    async def rollback(self) -> None: ...

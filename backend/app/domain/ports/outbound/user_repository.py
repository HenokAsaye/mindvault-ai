from __future__ import annotations
from abc import ABC, abstractmethod

from uuid import UUID

from app.domain.entities.user import User


class UserRepository(ABC):
    @abstractmethod
    async def create_user(self, *, user: User) -> User: ...
    @abstractmethod
    async def get_user_by_id(self, *, user_id: UUID) -> User | None: ...
    @abstractmethod
    async def get_user_by_email(self, *, email: str) -> User | None: ...
    @abstractmethod
    async def update_last_login(self, *, user_id: UUID) -> None: ...

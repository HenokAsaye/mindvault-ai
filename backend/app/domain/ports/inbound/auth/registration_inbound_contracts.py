from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID


@dataclass(slots=True)
class RegisterUserCommand:
    email: str
    password: str
    full_name: str
    organization_name: str


@dataclass(slots=True)
class RegisterUserResult:
    user_id: UUID
    default_org_id: UUID | None = None


class RegisterUserUseCase(ABC):
    @abstractmethod
    async def execute(self, command: RegisterUserCommand) -> RegisterUserResult: ...

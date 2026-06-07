from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(slots=True)
class LoginCommand:
    email: str
    password: str
    org_slug: str | None = None


@dataclass(slots=True)
class TokenPair:
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class LoginUseCase(ABC):
    @abstractmethod
    async def execute(self, command: LoginCommand) -> TokenPair: ...

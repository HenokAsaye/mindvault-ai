from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID


@dataclass(slots=True)
class SwitchOrganizationCommand:
    user_id: UUID
    target_org_id: UUID


@dataclass(slots=True)
class SwitchOrganizationResult:
    access_token: str
    refresh_token: str
    active_org_id: UUID


class SwitchOrganizationUseCase(ABC):
    @abstractmethod
    async def execute(
        self, command: SwitchOrganizationCommand
    ) -> SwitchOrganizationResult: ...

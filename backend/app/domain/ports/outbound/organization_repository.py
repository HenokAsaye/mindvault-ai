from __future__ import annotations
from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.entities.organization import Organization


class OrganizationRepository(ABC):
    @abstractmethod
    async def create_org(self, *, org: Organization) -> Organization: ...
    @abstractmethod
    async def get_org_by_id(self, *, org_id: UUID) -> Organization | None: ...
    @abstractmethod
    async def get_org_by_slug(self, *, slug: str) -> Organization | None: ...
    @abstractmethod
    async def exists_slug(self, *, slug: str) -> bool: ...

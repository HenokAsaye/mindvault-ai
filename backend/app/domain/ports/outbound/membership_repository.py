from __future__ import annotations
from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.entities.organization_membership import OrganizationMembership


class MembershipRepository(ABC):
    @abstractmethod
    async def create_membership(
        self, *, membership: OrganizationMembership
    ) -> OrganizationMembership: ...

    @abstractmethod
    async def get_active_membership(
        self, *, user_id: UUID, org_id: UUID
    ) -> OrganizationMembership | None: ...

    @abstractmethod
    async def get_membership_by_org_slug(
        self, *, org_slug: str, user_id: UUID
    ) -> OrganizationMembership | None: ...

    @abstractmethod
    async def list_user_memberships(
        self, *, user_id: UUID
    ) -> list[OrganizationMembership]: ...

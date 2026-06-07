from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.outbound.db.sqlalchemy_models import (
    OrganizationMembershipORM,
    OrganizationORM,
)
from app.domain.entities.organization_membership import OrganizationMembership
from app.domain.ports.outbound.membership_repository import MembershipRepository
from app.domain.value_objects.membership_status import MembershipStatus
from app.domain.value_objects.user_role import UserRole


def _to_domain(model: OrganizationMembershipORM) -> OrganizationMembership:
    return OrganizationMembership(
        id=UUID(model.id) if isinstance(model.id, str) else model.id,
        org_id=UUID(model.org_id) if isinstance(model.org_id, str) else model.org_id,
        user_id=(
            UUID(model.user_id) if isinstance(model.user_id, str) else model.user_id
        ),
        role=UserRole(model.role),
        status=MembershipStatus(model.status),
        joined_at=model.joined_at,
        invited_by_user_id=(
            UUID(model.invited_by_user_id)
            if isinstance(model.invited_by_user_id, str) and model.invited_by_user_id
            else None
        ),
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


class MembershipRepositoryImpl(MembershipRepository):
    def __init__(self, *, db: AsyncSession) -> None:
        self._db = db

    async def create_membership(
        self, *, membership: OrganizationMembership
    ) -> OrganizationMembership:
        row = OrganizationMembershipORM(
            id=membership.id,
            org_id=membership.org_id,
            user_id=membership.user_id,
            role=str(membership.role),
            status=str(membership.status),
            joined_at=membership.joined_at,
            invited_by_user_id=membership.invited_by_user_id,
        )
        self._db.add(row)
        await self._db.flush()
        return _to_domain(row)

    async def get_active_membership(
        self, *, user_id: UUID, org_id: UUID
    ) -> OrganizationMembership | None:
        result = await self._db.execute(
            select(OrganizationMembershipORM).where(
                OrganizationMembershipORM.user_id == user_id,
                OrganizationMembershipORM.org_id == org_id,
                OrganizationMembershipORM.status == MembershipStatus.ACTIVE.value,
            )
        )
        row = result.scalar_one_or_none()
        return _to_domain(row) if row else None

    async def get_membership_by_org_slug(
        self, *, org_slug: str, user_id: UUID
    ) -> OrganizationMembership | None:
        result = await self._db.execute(
            select(OrganizationMembershipORM)
            .join(
                OrganizationORM, OrganizationORM.id == OrganizationMembershipORM.org_id
            )
            .where(
                OrganizationMembershipORM.user_id == user_id,
                OrganizationMembershipORM.status == MembershipStatus.ACTIVE.value,
                OrganizationORM.slug == org_slug,
            )
        )
        row = result.scalar_one_or_none()
        return _to_domain(row) if row else None

    async def list_user_memberships(
        self, *, user_id: UUID
    ) -> list[OrganizationMembership]:
        result = await self._db.execute(
            select(OrganizationMembershipORM).where(
                OrganizationMembershipORM.user_id == user_id,
                OrganizationMembershipORM.status == MembershipStatus.ACTIVE.value,
            )
        )
        rows = result.scalars().all()
        return [_to_domain(row) for row in rows]

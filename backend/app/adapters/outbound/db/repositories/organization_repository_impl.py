from __future__ import annotations
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.outbound.db.sqlalchemy_models import OrganizationORM
from app.domain.entities.organization import Organization
from app.domain.ports.outbound.organization_repository import OrganizationRepository


def _to_domain(model: OrganizationORM) -> Organization:
    return Organization(
        id=UUID(model.id) if isinstance(model.id, str) else model.id,
        name=model.name,
        slug=model.slug,
        api_key_hash=model.api_key_hash,
        metadata=model.metadata_json or {},
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


class OrganizationRepositoryImpl(OrganizationRepository):
    def __init__(self, *, db: AsyncSession) -> None:
        self._db = db

    async def create_org(self, *, org: Organization) -> Organization:
        row = OrganizationORM(
            id=org.id,
            name=org.name,
            slug=org.slug,
            api_key_hash=org.api_key_hash,
            metadata_json=org.metadata,
        )
        self._db.add(row)
        await self._db.flush()
        return _to_domain(row)

    async def get_org_by_id(self, *, org_id: UUID) -> Organization | None:
        row = await self._db.get(OrganizationORM, org_id)
        return _to_domain(row) if row else None

    async def get_org_by_slug(self, *, slug: str) -> Organization | None:
        result = await self._db.execute(
            select(OrganizationORM).where(OrganizationORM.slug == slug)
        )
        row = result.scalar_one_or_none()
        return _to_domain(row) if row else None

    async def exists_slug(self, *, slug: str) -> bool:
        result = await self._db.execute(
            select(OrganizationORM.id).where(OrganizationORM.slug == slug)
        )
        return result.scalar_one_or_none() is not None

from __future__ import annotations
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.outbound.db.sqlalchemy_models import UserORM
from app.domain.entities.user import User
from app.domain.ports.outbound.user_repository import UserRepository

def _to_domain(model: UserORM) -> User:
    return User(
        id=model.id,
        email=model.email,
        full_name=model.full_name,
        password_hash=model.password_hash,
        is_active=model.is_active,
        is_platform_admin=model.is_platform_admin,
        mfa_enabled=model.mfa_enabled,
        email_verified_at=model.email_verified_at,
        last_login_at=model.last_login_at,
        metadata=model.metadata_json or {},
        created_at=model.created_at,
        updated_at=model.updated_at,
    )

class UserRepositoryImpl(UserRepository):
    def __init__(self, *, db: AsyncSession) -> None:
        self._db = db

    async def create_user(self, *, user: User) -> User:
        row = UserORM(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            password_hash=user.password_hash,
            is_active=user.is_active,
            is_platform_admin=user.is_platform_admin,
            mfa_enabled=user.mfa_enabled,
            email_verified_at=user.email_verified_at,
            last_login_at=user.last_login_at,
            metadata_json=user.metadata,
        )
        self._db.add(row)
        await self._db.flush()
        return _to_domain(row)

    async def get_user_by_id(self, *, user_id: UUID) -> User | None:
        row = await self._db.get(UserORM, user_id)
        return _to_domain(row) if row else None

    async def get_user_by_email(self, *, email: str) -> User | None:
        result = await self._db.execute(select(UserORM).where(UserORM.email == email))
        row = result.scalar_one_or_none()
        return _to_domain(row) if row else None

    async def update_last_login(self, *, user_id: UUID) -> None:
        row = await self._db.get(UserORM, user_id)
        if row:
            row.last_login_at = datetime.now(timezone.utc)
            await self._db.flush()

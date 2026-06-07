from __future__ import annotations

from datetime import datetime, timedelta, timezone
from urllib.parse import quote
from uuid import UUID, uuid4

from sqlalchemy import delete, func, select
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import async_sessionmaker
from app.adapters.outbound.db.sqlalchemy_models import (
    AuditLogORM,
    OrganizationInvitationORM,
    OrganizationORM,
    OrganizationMembershipORM,
    RefreshTokenORM,
    UserORM,
)
from app.domain.value_objects.membership_status import MembershipStatus
from app.domain.value_objects.user_role import UserRole
from app.infrastructure.security.redis_services import (
    InvitationService,
    ThrottleService,
    TokenService,
)

_INVITE_ROLE_VALUES = frozenset(
    {UserRole.OWNER.value, UserRole.ADMIN.value, UserRole.MEMBER.value}
)

class IAMService:
    def __init__(
        self,
        *,
        session_factory: async_sessionmaker,
        token_service: TokenService,
        throttle_service: ThrottleService,
        invitation_service: InvitationService,
        password_hasher,
        frontend_base_url: str,
        access_ttl_seconds: int,
        refresh_ttl_seconds: int,
        mfa_attempt_ttl_seconds: int,
    ) -> None:
        self._session_factory = session_factory
        self._token_service = token_service
        self._throttle_service = throttle_service
        self._invitation_service = invitation_service
        self._password_hasher = password_hasher
        self._frontend_base_url = frontend_base_url.rstrip("/")
        self._access_ttl_seconds = access_ttl_seconds
        self._refresh_ttl_seconds = refresh_ttl_seconds
        self._mfa_attempt_ttl_seconds = mfa_attempt_ttl_seconds

    async def _audit(
        self,
        *,
        event_type: str,
        actor_id: UUID | None,
        org_id: UUID | None,
        ip_address: str | None,
        user_agent: str | None,
        metadata: dict | None = None,
        target_user_id: UUID | None = None,
    ) -> None:
        async with self._session_factory() as session:
            session.add(
                AuditLogORM(
                    id=uuid4(),
                    event_type=event_type,
                    actor_id=actor_id,
                    org_id=org_id,
                    target_user_id=target_user_id,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    metadata_json=metadata or {},
                )
            )
            await session.commit()

    async def login(
        self,
        *,
        email: str,
        password: str,
        org_slug: str | None,
        ip_address: str | None,
        user_agent: str | None,
    ) -> dict:
        ip = ip_address or "unknown"
        async with self._session_factory() as session:
            user = (
                await session.execute(
                    select(UserORM).where(UserORM.email == email.lower())
                )
            ).scalar_one_or_none()
            if (
                not user
                or not user.password_hash
                or not self._password_hasher.verify_password(
                    plain_password=password, hashed_password=user.password_hash
                )
            ):
                throttle = await self._throttle_service.register_login_failure(
                    ip=ip, username=email
                )
                await self._audit(
                    event_type="LOGIN_FAIL",
                    actor_id=user.id if user else None,
                    org_id=None,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    metadata=throttle,
                )
                raise ValueError("Invalid credentials")
            if not user.is_active:
                raise ValueError("User account is disabled")

            membership_stmt = select(OrganizationMembershipORM).where(
                OrganizationMembershipORM.user_id == user.id,
                OrganizationMembershipORM.status == MembershipStatus.ACTIVE.value,
            )
            if org_slug:
                membership_stmt = membership_stmt.join(
                    OrganizationORM,
                    OrganizationORM.id == OrganizationMembershipORM.org_id,
                ).where(OrganizationORM.slug == org_slug)
            memberships = (await session.execute(membership_stmt)).scalars().all()
            membership = memberships[0] if memberships else None
            if not membership:
                raise ValueError("No active organization membership")

            await self._throttle_service.clear_login_failures(ip=ip, username=email)
            user.last_login_at = datetime.now(timezone.utc)
            await session.commit()

            if user.mfa_enabled:
                mfa_token = await self._token_service.issue_access(
                    claims={
                        "sub": str(user.id),
                        "org_id": str(membership.org_id),
                        "role": str(membership.role),
                        "mfa": "pending",
                    },
                    ttl_seconds=self._mfa_attempt_ttl_seconds,
                )
                return {
                    "mfa_required": True,
                    "mfa_attempt_token": mfa_token,
                    "expires_in_seconds": self._mfa_attempt_ttl_seconds,
                }

            claims = {
                "sub": str(user.id),
                "org_id": str(membership.org_id),
                "role": str(membership.role),
            }
            access = await self._token_service.issue_access(
                claims=claims, ttl_seconds=self._access_ttl_seconds
            )
            refresh, refresh_jti, family = await self._token_service.issue_refresh(
                claims=claims, ttl_seconds=self._refresh_ttl_seconds
            )
            session.add(
                RefreshTokenORM(
                    id=uuid4(),
                    user_id=user.id,
                    org_id=membership.org_id,
                    token_family=family,
                    jti=refresh_jti,
                    expires_at=datetime.now(timezone.utc)
                    + timedelta(seconds=self._refresh_ttl_seconds),
                )
            )
            await session.commit()
            await self._audit(
                event_type="LOGIN_SUCCESS",
                actor_id=user.id,
                org_id=membership.org_id,
                ip_address=ip_address,
                user_agent=user_agent,
            )
            return {
                "access_token": access,
                "refresh_token": refresh,
                "token_type": "bearer",
            }

    async def refresh(self, *, refresh_token: str) -> dict:
        claims = self._token_service.decode(refresh_token)
        rotated = await self._token_service.rotate_refresh(
            presented_jti=claims["jti"],
            user_id=claims["sub"],
            org_id=claims["org_id"],
            role=claims["role"],
            access_ttl=self._access_ttl_seconds,
            refresh_ttl=self._refresh_ttl_seconds,
        )
        return {
            "access_token": rotated["access_token"],
            "refresh_token": rotated["refresh_token"],
            "token_type": "bearer",
        }

    async def logout(self, *, access_claims: dict) -> None:
        exp = int(access_claims["exp"])
        now = int(datetime.now(timezone.utc).timestamp())
        await self._token_service.revoke_access(
            jti=access_claims["jti"], ttl_seconds=max(1, exp - now)
        )

    async def create_invitation(
        self,
        *,
        actor_claims: dict,
        org_id: UUID,
        email: str,
        role: str,
        ttl_seconds: int,
    ) -> dict[str, str]:
        if str(actor_claims["org_id"]) != str(org_id):
            raise ValueError("Cross-tenant access denied")

        role_key = role.strip().lower()
        if role_key not in _INVITE_ROLE_VALUES:
            raise ValueError("Invalid role for invitation")

        email_norm = email.strip().lower()
        actor_user_id = UUID(str(actor_claims["sub"]))
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(seconds=ttl_seconds)
        invite_id = uuid4()

        async with self._session_factory() as session:
            org = (
                await session.execute(
                    select(OrganizationORM).where(OrganizationORM.id == org_id)
                )
            ).scalar_one_or_none()
            if not org:
                raise ValueError("Organization not found")

            existing_user = (
                await session.execute(
                    select(UserORM).where(UserORM.email == email_norm)
                )
            ).scalar_one_or_none()
            if existing_user:
                ms = (
                    await session.execute(
                        select(OrganizationMembershipORM).where(
                            OrganizationMembershipORM.org_id == org_id,
                            OrganizationMembershipORM.user_id == existing_user.id,
                            OrganizationMembershipORM.status
                            == MembershipStatus.ACTIVE.value,
                        )
                    )
                ).scalar_one_or_none()
                if ms:
                    raise ValueError(
                        "User is already an active member of this organization"
                    )

            await session.execute(
                delete(OrganizationInvitationORM).where(
                    OrganizationInvitationORM.org_id == org_id,
                    OrganizationInvitationORM.email == email_norm,
                    OrganizationInvitationORM.consumed_at.is_(None),
                )
            )

            session.add(
                OrganizationInvitationORM(
                    id=invite_id,
                    org_id=org_id,
                    email=email_norm,
                    role=role_key,
                    invited_by_user_id=actor_user_id,
                    expires_at=expires_at,
                )
            )
            await session.commit()

        token = self._invitation_service.issue(
            invite_id=str(invite_id),
            org_id=str(org_id),
            email=email_norm,
            role=role_key,
            expires_in_seconds=ttl_seconds,
        )

        encoded = quote(token, safe="")
        invite_url = f"{self._frontend_base_url}/invitations/accept?token={encoded}"
        hours = max(1, ttl_seconds // 3600)

        display_role = role.strip().upper()

        return {
            "invitation_token": token,
            "invite_url": invite_url,
            "organization_name": org.name,
            "to_email": email_norm,
            "display_role": display_role,
            "expires_in_hours": hours,
        }

    async def accept_invitation(self, *, token: str, user_id: UUID) -> None:
        payload = self._invitation_service.verify(token)
        invite_uuid = UUID(payload["invite_id"])
        now = datetime.now(timezone.utc)

        async with self._session_factory() as session:
            inv = (
                await session.execute(
                    select(OrganizationInvitationORM)
                    .where(OrganizationInvitationORM.id == invite_uuid)
                    .with_for_update()
                )
            ).scalar_one_or_none()
            if not inv:
                raise ValueError("Invitation not found or no longer valid")
            if inv.consumed_at is not None:
                raise ValueError("Invitation already used")
            if inv.expires_at <= now:
                raise ValueError("Invitation expired")
            if (
                str(inv.org_id) != payload["org_id"]
                or inv.email != payload["email"]
                or inv.role != payload["role"]
            ):
                raise ValueError("Invitation data mismatch")

            user = (
                await session.execute(select(UserORM).where(UserORM.id == user_id))
            ).scalar_one_or_none()
            if not user:
                raise ValueError("User not found")
            if user.email.strip().lower() != inv.email:
                raise ValueError(
                    "Invitation was sent to a different email address; "
                    "sign in with that email"
                )

            existing = (
                await session.execute(
                    select(OrganizationMembershipORM).where(
                        OrganizationMembershipORM.org_id == inv.org_id,
                        OrganizationMembershipORM.user_id == user_id,
                    )
                )
            ).scalar_one_or_none()

            joined = now
            if existing:
                existing.status = MembershipStatus.ACTIVE.value
                existing.role = inv.role
                existing.joined_at = joined
                if inv.invited_by_user_id:
                    existing.invited_by_user_id = inv.invited_by_user_id
            else:
                session.add(
                    OrganizationMembershipORM(
                        id=uuid4(),
                        org_id=inv.org_id,
                        user_id=user_id,
                        role=inv.role,
                        status=MembershipStatus.ACTIVE.value,
                        joined_at=joined,
                        invited_by_user_id=inv.invited_by_user_id,
                    )
                )

            inv.consumed_at = now
            await session.commit()

    async def register_via_invitation(
        self, *, token: str, password: str, full_name: str
    ) -> dict[str, str]:
        payload = self._invitation_service.verify(token)
        invite_uuid = UUID(payload["invite_id"])
        email_norm = payload["email"].strip().lower()
        now = datetime.now(timezone.utc)

        async with self._session_factory() as session:
            inv = (
                await session.execute(
                    select(OrganizationInvitationORM)
                    .where(OrganizationInvitationORM.id == invite_uuid)
                    .with_for_update()
                )
            ).scalar_one_or_none()
            if not inv:
                raise ValueError("Invitation not found or no longer valid")
            if inv.consumed_at is not None:
                raise ValueError("Invitation already used")
            if inv.expires_at <= now:
                raise ValueError("Invitation expired")
            if (
                str(inv.org_id) != payload["org_id"]
                or inv.email != email_norm
                or inv.role != payload["role"]
            ):
                raise ValueError("Invitation data mismatch")

            existing_user = (
                await session.execute(
                    select(UserORM).where(UserORM.email == email_norm)
                )
            ).scalar_one_or_none()
            if existing_user:
                raise ValueError(
                    "An account already exists for this email; sign in and accept "
                    "the invitation"
                )

            new_user_id = uuid4()
            session.add(
                UserORM(
                    id=new_user_id,
                    email=email_norm,
                    full_name=full_name.strip(),
                    password_hash=self._password_hasher.hash_password(
                        plain_password=password
                    ),
                    is_active=True,
                    is_platform_admin=False,
                    mfa_enabled=False,
                    metadata_json={},
                )
            )
            await session.flush()
            session.add(
                OrganizationMembershipORM(
                    id=uuid4(),
                    org_id=inv.org_id,
                    user_id=new_user_id,
                    role=inv.role,
                    status=MembershipStatus.ACTIVE.value,
                    joined_at=now,
                    invited_by_user_id=inv.invited_by_user_id,
                )
            )
            inv.consumed_at = now
            try:
                await session.commit()
            except IntegrityError as exc:
                await session.rollback()
                raise ValueError(
                    "Failed to complete invitation registration due to data "
                    "integrity constraints"
                ) from exc
            return {"user_id": str(new_user_id), "default_org_id": str(inv.org_id)}

    async def list_org_members(
        self, *, actor_claims: dict, org_id: UUID, page: int, page_size: int
    ) -> dict:
        if str(actor_claims["org_id"]) != str(org_id):
            raise ValueError("Cross-tenant access denied")
        offset = max(0, (page - 1) * page_size)
        async with self._session_factory() as session:
            rows = (
                (
                    await session.execute(
                        select(OrganizationMembershipORM)
                        .options(selectinload(OrganizationMembershipORM.user))
                        .where(OrganizationMembershipORM.org_id == org_id)
                        .order_by(OrganizationMembershipORM.created_at.desc())
                        .offset(offset)
                        .limit(page_size)
                    )
                )
                .scalars()
                .all()
            )
            total = (
                await session.execute(
                    select(func.count())
                    .select_from(OrganizationMembershipORM)
                    .where(OrganizationMembershipORM.org_id == org_id)
                )
            ).scalar_one()
        items = [
            {
                "full_name": str(r.user.full_name) if r.user else None,
                "email": str(r.user.email) if r.user else None,
                "user_id": str(r.user_id),
                "org_id": str(r.org_id),
                "role": r.role.upper(),
                "status": r.status.upper(),
            }
            for r in rows
        ]
        return {
            "items": items,
            "total": int(total),
            "page": page,
            "page_size": page_size,
        }

    async def patch_member(
        self,
        *,
        actor_claims: dict,
        org_id: UUID,
        user_id: UUID,
        role: str | None,
        status: str | None,
    ) -> dict:
        if str(actor_claims["org_id"]) != str(org_id):
            raise ValueError("Cross-tenant access denied")
        async with self._session_factory() as session:
            row = (
                await session.execute(
                    select(OrganizationMembershipORM).where(
                        OrganizationMembershipORM.org_id == org_id,
                        OrganizationMembershipORM.user_id == user_id,
                    )
                )
            ).scalar_one_or_none()
            if not row:
                raise ValueError("Membership not found")
            if role:
                row.role = role.lower()
            if status:
                row.status = status.lower()
            await session.commit()
            return {
                "user_id": str(row.user_id),
                "org_id": str(row.org_id),
                "role": row.role.upper(),
                "status": row.status.upper(),
            }

    async def delete_member(
        self, *, actor_claims: dict, org_id: UUID, user_id: UUID
    ) -> None:
        if str(actor_claims["org_id"]) != str(org_id):
            raise ValueError("Cross-tenant access denied")
        async with self._session_factory() as session:
            await session.execute(
                delete(OrganizationMembershipORM).where(
                    OrganizationMembershipORM.org_id == org_id,
                    OrganizationMembershipORM.user_id == user_id,
                )
            )
            await session.commit()

    async def list_my_organizations(
        self, *, actor_claims: dict, page: int, page_size: int
    ) -> dict:
        user_id = actor_claims["sub"]
        offset = max(0, (page - 1) * page_size)
        async with self._session_factory() as session:
            rows = (
                await session.execute(
                    select(OrganizationORM, OrganizationMembershipORM.role)
                    .join(
                        OrganizationMembershipORM,
                        OrganizationMembershipORM.org_id == OrganizationORM.id,
                    )
                    .where(
                        OrganizationMembershipORM.user_id == user_id,
                        OrganizationMembershipORM.status
                        == MembershipStatus.ACTIVE.value,
                    )
                    .order_by(OrganizationORM.created_at.desc())
                    .offset(offset)
                    .limit(page_size)
                )
            ).all()
            total = (
                await session.execute(
                    select(func.count())
                    .select_from(OrganizationMembershipORM)
                    .where(
                        OrganizationMembershipORM.user_id == user_id,
                        OrganizationMembershipORM.status
                        == MembershipStatus.ACTIVE.value,
                    )
                )
            ).scalar_one()
        items = [
            {
                "id": str(r.id),
                "name": str(r.name),
                "slug": str(r.slug),
                "role": role.upper(),
            }
            for r, role in rows
        ]
        return {
            "items": items,
            "total": int(total),
            "page": page,
            "page_size": page_size,
        }

from __future__ import annotations
import re
from uuid import uuid4
import secrets

from app.domain.entities.organization import Organization
from app.domain.entities.organization_membership import OrganizationMembership
from app.domain.entities.user import User
from app.domain.ports.inbound.auth.registration_inbound_contracts import (
    RegisterUserCommand,
    RegisterUserResult,
    RegisterUserUseCase,
)
from app.domain.ports.outbound.password_hasher import PasswordHasher
from app.domain.value_objects.membership_status import MembershipStatus
from app.domain.value_objects.user_role import UserRole


class RegisterUserService(RegisterUserUseCase):
    def __init__(self, *, uow_factory, password_hasher: PasswordHasher) -> None:
        self._uow_factory = uow_factory
        self._password_hasher = password_hasher

    def slugify_org_name(self, name: str) -> str:
        slug = name.lower().replace(" ", "-")
        slug = re.sub(r"[^a-z0-9\-]", "", slug)
        return slug

    async def _build_unique_org_slug(self, *, uow, org_name: str) -> str:
        base_slug = self.slugify_org_name(org_name)
        slug = base_slug

        if not await uow.organizations.exists_slug(slug=slug):
            return slug

        for _ in range(10):
            slug = f"{base_slug}-{secrets.token_hex(4)}"
            if not await uow.organizations.exists_slug(slug=slug):
                return slug

        raise ValueError("Could not generate a unique organization slug")

    async def execute(self, command: RegisterUserCommand) -> RegisterUserResult:
        async with self._uow_factory() as uow:
            existing = await uow.users.get_user_by_email(email=command.email)
            if existing:
                raise ValueError("Email already exists")

            if not command.organization_name:
                raise ValueError("Organization name is required")

            slug = await self._build_unique_org_slug(
                uow=uow, org_name=command.organization_name
            )
            org = Organization(
                id=uuid4(),
                name=command.organization_name,
                slug=slug,
            )
            await uow.organizations.create_org(org=org)

            user = User(
                id=uuid4(),
                email=command.email,
                full_name=command.full_name,
                password_hash=self._password_hasher.hash_password(
                    plain_password=command.password
                ),
            )
            await uow.users.create_user(user=user)

            membership = OrganizationMembership(
                id=uuid4(),
                org_id=org.id,
                user_id=user.id,
                role=UserRole.OWNER,
                status=MembershipStatus.ACTIVE,
            )
            await uow.memberships.create_membership(membership=membership)

            await uow.commit()
            return RegisterUserResult(user_id=user.id, default_org_id=org.id)

"""Unit tests for JWT-based login use case."""

from __future__ import annotations

from uuid import uuid4

import pytest

from app.adapters.outbound.db.repositories.password_hasher_impl import (
    BcryptPasswordHasher,
)
from app.adapters.outbound.db.repositories.token_provider_impl import JwtTokenProvider
from app.application.use_cases.login_user_service import LoginUserService
from app.domain.entities.organization_membership import OrganizationMembership
from app.domain.entities.user import User
from app.domain.ports.inbound.auth.login_inbound_contracts import LoginCommand
from app.domain.value_objects.membership_status import MembershipStatus
from app.domain.value_objects.user_role import UserRole
from tests.helpers.mocks import FakeMembershipRepo, FakeUoW, FakeUserRepo, uow_factory


@pytest.mark.unit
@pytest.mark.asyncio
async def test_login_returns_token_pair() -> None:
    user_id = uuid4()
    org_id = uuid4()
    hasher = BcryptPasswordHasher()
    password = "login-pass-99"
    uow = FakeUoW(
        users=FakeUserRepo(
            by_email={
                "user@example.com": User(
                    id=user_id,
                    email="user@example.com",
                    full_name="User",
                    password_hash=hasher.hash_password(plain_password=password),
                )
            }
        ),
        memberships=FakeMembershipRepo(
            memberships=[
                OrganizationMembership(
                    id=uuid4(),
                    org_id=org_id,
                    user_id=user_id,
                    role=UserRole.MEMBER,
                    status=MembershipStatus.ACTIVE,
                )
            ]
        ),
    )
    token_provider = JwtTokenProvider(secret="test-secret", issuer="t", audience="t")
    service = LoginUserService(
        uow_factory=uow_factory(uow),
        password_hasher=hasher,
        token_provider=token_provider,
        access_token_ttl_seconds=3600,
        refresh_token_ttl_seconds=604800,
    )
    result = await service.execute(
        LoginCommand(email="user@example.com", password=password)
    )
    assert result.access_token
    assert result.refresh_token
    assert uow.committed


@pytest.mark.unit
@pytest.mark.asyncio
async def test_login_invalid_password() -> None:
    hasher = BcryptPasswordHasher()
    uow = FakeUoW(
        users=FakeUserRepo(
            by_email={
                "u@x.com": User(
                    id=uuid4(),
                    email="u@x.com",
                    full_name="U",
                    password_hash=hasher.hash_password(plain_password="right"),
                )
            }
        ),
    )
    service = LoginUserService(
        uow_factory=uow_factory(uow),
        password_hasher=hasher,
        token_provider=JwtTokenProvider(secret="s"),
        access_token_ttl_seconds=60,
        refresh_token_ttl_seconds=60,
    )
    with pytest.raises(ValueError, match="Invalid credentials"):
        await service.execute(LoginCommand(email="u@x.com", password="wrong"))

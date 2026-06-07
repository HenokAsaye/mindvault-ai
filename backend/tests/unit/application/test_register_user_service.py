"""Unit tests for user registration use case."""

from __future__ import annotations

from uuid import uuid4

import pytest

from app.application.use_cases.register_user_service import RegisterUserService
from app.domain.entities.user import User
from app.domain.ports.inbound.auth.registration_inbound_contracts import (
    RegisterUserCommand,
)
from tests.helpers.mocks import FakeUoW, uow_factory


@pytest.fixture
def password_hasher():
    from app.adapters.outbound.db.repositories.password_hasher_impl import (
        BcryptPasswordHasher,
    )

    return BcryptPasswordHasher()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_register_creates_user_org_and_membership(password_hasher) -> None:
    uow = FakeUoW()
    service = RegisterUserService(
        uow_factory=uow_factory(uow), password_hasher=password_hasher
    )
    result = await service.execute(
        RegisterUserCommand(
            email="new@example.com",
            password="secure-pass-123",
            full_name="New User",
            organization_name="Acme Corp",
        )
    )
    assert result.user_id is not None
    assert result.default_org_id is not None
    assert uow.committed
    assert len(uow.users.created) == 1
    assert len(uow.organizations.orgs) == 1


@pytest.mark.unit
@pytest.mark.asyncio
async def test_register_rejects_duplicate_email(password_hasher) -> None:
    uow = FakeUoW()
    uow.users.by_email["dup@example.com"] = User(
        id=uuid4(), email="dup@example.com", full_name="Existing"
    )
    service = RegisterUserService(
        uow_factory=uow_factory(uow), password_hasher=password_hasher
    )
    with pytest.raises(ValueError, match="Email already exists"):
        await service.execute(
            RegisterUserCommand(
                email="dup@example.com",
                password="x",
                full_name="X",
                organization_name="Org",
            )
        )


@pytest.mark.unit
@pytest.mark.asyncio
async def test_register_requires_organization_name(password_hasher) -> None:
    uow = FakeUoW()
    service = RegisterUserService(
        uow_factory=uow_factory(uow), password_hasher=password_hasher
    )
    with pytest.raises(ValueError, match="Organization name"):
        await service.execute(
            RegisterUserCommand(
                email="a@b.com",
                password="x",
                full_name="X",
                organization_name="",
            )
        )


@pytest.mark.unit
def test_slugify_org_name(password_hasher) -> None:
    service = RegisterUserService(
        uow_factory=lambda: FakeUoW(), password_hasher=password_hasher
    )
    assert service.slugify_org_name("Acme Corp!") == "acme-corp"

"""Unit tests for organization switch use case."""

from __future__ import annotations

from uuid import uuid4

import pytest

from app.adapters.outbound.db.repositories.token_provider_impl import JwtTokenProvider
from app.application.use_cases.switch_org_service import SwitchOrganizationService
from app.domain.entities.organization_membership import OrganizationMembership
from app.domain.ports.inbound.auth.org_switch_inbound_contracts import (
    SwitchOrganizationCommand,
)
from app.domain.value_objects.membership_status import MembershipStatus
from app.domain.value_objects.user_role import UserRole
from tests.helpers.mocks import FakeMembershipRepo, FakeUoW, uow_factory


@pytest.mark.unit
@pytest.mark.asyncio
async def test_switch_org_issues_new_tokens() -> None:
    user_id = uuid4()
    org_id = uuid4()
    uow = FakeUoW(
        memberships=FakeMembershipRepo(
            memberships=[
                OrganizationMembership(
                    id=uuid4(),
                    org_id=org_id,
                    user_id=user_id,
                    role=UserRole.ADMIN,
                    status=MembershipStatus.ACTIVE,
                )
            ]
        )
    )
    service = SwitchOrganizationService(
        uow_factory=uow_factory(uow),
        token_provider=JwtTokenProvider(secret="switch-secret"),
        access_token_ttl_seconds=3600,
        refresh_token_ttl_seconds=86400,
    )
    result = await service.execute(
        SwitchOrganizationCommand(user_id=user_id, target_org_id=org_id)
    )
    assert result.access_token
    assert result.refresh_token
    assert result.active_org_id == org_id


@pytest.mark.unit
@pytest.mark.asyncio
async def test_switch_org_denies_without_membership() -> None:
    service = SwitchOrganizationService(
        uow_factory=uow_factory(FakeUoW()),
        token_provider=JwtTokenProvider(secret="s"),
        access_token_ttl_seconds=60,
        refresh_token_ttl_seconds=60,
    )
    with pytest.raises(ValueError, match="does not have access"):
        await service.execute(
            SwitchOrganizationCommand(user_id=uuid4(), target_org_id=uuid4())
        )

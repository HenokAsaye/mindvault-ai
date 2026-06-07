"""Integration tests for auth API routes."""

from __future__ import annotations

from uuid import uuid4

import pytest

from app.domain.ports.inbound.auth.org_switch_inbound_contracts import (
    SwitchOrganizationResult,
)
from app.domain.ports.inbound.auth.registration_inbound_contracts import (
    RegisterUserResult,
)
from app.infrastructure.di.container import Container
from app.main import app

@pytest.mark.integration
def test_register_success(api_client, monkeypatch) -> None:
    class FakeRegister:
        async def execute(self, command):
            return RegisterUserResult(user_id=uuid4(), default_org_id=uuid4())

    app.dependency_overrides[Container.get_register_user_service] = (
        lambda: FakeRegister()
    )
    response = api_client.post(
        "/api/v1/auth/register",
        json={
            "email": "new@test.com",
            "password": "password123",
            "full_name": "Test",
            "organization_name": "Test Org",
        },
    )
    app.dependency_overrides.pop(Container.get_register_user_service, None)
    assert response.status_code == 200
    data = response.json()
    assert "user_id" in data
    assert "default_org_id" in data

@pytest.mark.integration
def test_register_conflict_on_duplicate(api_client) -> None:
    class FailingRegister:
        async def execute(self, command):
            raise ValueError("Email already exists")

    app.dependency_overrides[Container.get_register_user_service] = (
        lambda: FailingRegister()
    )
    response = api_client.post(
        "/api/v1/auth/register",
        json={
            "email": "dup@test.com",
            "password": "password123",
            "full_name": "Test",
            "organization_name": "Org",
        },
    )
    app.dependency_overrides.pop(Container.get_register_user_service, None)
    assert response.status_code == 409

@pytest.mark.integration
def test_login_success(api_client) -> None:
    class FakeIAM:
        async def login(self, **kwargs):
            return {
                "access_token": "access",
                "refresh_token": "refresh",
                "token_type": "bearer",
            }

    app.dependency_overrides[Container.get_iam_service] = lambda: FakeIAM()
    response = api_client.post(
        "/api/v1/auth/login",
        json={"email": "u@test.com", "password": "password123"},
    )
    app.dependency_overrides.pop(Container.get_iam_service, None)
    assert response.status_code == 200
    assert response.json()["access_token"] == "access"

@pytest.mark.integration
def test_me_requires_auth(api_client) -> None:
    response = api_client.get("/api/v1/auth/me")
    assert response.status_code == 401

@pytest.mark.integration
def test_me_returns_claims(authed_client, auth_claims) -> None:
    response = authed_client.get("/api/v1/auth/me")
    assert response.status_code == 200
    body = response.json()
    assert body["user_id"] == auth_claims["sub"]
    assert body["org_id"] == auth_claims["org_id"]

@pytest.mark.integration
def test_switch_org(authed_client, test_user_id, test_org_id) -> None:
    class FakeSwitch:
        async def execute(self, command):
            return SwitchOrganizationResult(
                access_token="new-access",
                refresh_token="new-refresh",
                active_org_id=command.target_org_id,
            )

    app.dependency_overrides[Container.get_switch_org_service] = lambda: FakeSwitch()
    response = authed_client.post(
        "/api/v1/auth/switch-org",
        json={"target_org_id": str(test_org_id)},
        headers={"Authorization": "Bearer fake"},
    )
    app.dependency_overrides.pop(Container.get_switch_org_service, None)
    assert response.status_code == 200
    assert response.json()["access_token"] == "new-access"

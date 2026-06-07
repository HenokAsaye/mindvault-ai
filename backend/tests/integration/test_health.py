"""Integration tests for system health endpoint."""

from __future__ import annotations

import pytest


@pytest.mark.integration
def test_health_returns_ok(api_client) -> None:
    response = api_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

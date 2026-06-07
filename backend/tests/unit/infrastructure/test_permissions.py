"""Unit tests for role-based permission dependency."""

from __future__ import annotations

import pytest
from fastapi import HTTPException

from app.infrastructure.security.permissions import requires_role


@pytest.mark.unit
def test_requires_role_allows_matching_role() -> None:
    dep = requires_role("owner", "admin")
    claims = dep(claims={"role": "owner", "sub": "1"})
    assert claims["role"] == "owner"


@pytest.mark.unit
def test_requires_role_denies_insufficient_role() -> None:
    dep = requires_role("owner")
    with pytest.raises(HTTPException) as exc:
        dep(claims={"role": "viewer"})
    assert exc.value.status_code == 403

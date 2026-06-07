"""Unit tests for domain value objects and enums."""

from __future__ import annotations

import pytest

from app.domain.entities.document import DocumentStatus
from app.domain.value_objects.membership_status import MembershipStatus
from app.domain.value_objects.user_role import UserRole

@pytest.mark.unit
class TestUserRole:
    def test_roles_are_strings(self) -> None:
        assert UserRole.OWNER == "owner"
        assert UserRole.ADMIN == "admin"
        assert UserRole.MEMBER == "member"
        assert UserRole.VIEWER == "viewer"

@pytest.mark.unit
class TestMembershipStatus:
    def test_status_values(self) -> None:
        assert MembershipStatus.INVITED == "invited"
        assert MembershipStatus.ACTIVE == "active"
        assert MembershipStatus.SUSPENDED == "suspended"

@pytest.mark.unit
class TestDocumentStatus:
    def test_lifecycle_values(self) -> None:
        assert DocumentStatus.PENDING.value == "pending"
        assert DocumentStatus.PROCESSING.value == "processing"
        assert DocumentStatus.READY.value == "ready"
        assert DocumentStatus.FAILED.value == "failed"

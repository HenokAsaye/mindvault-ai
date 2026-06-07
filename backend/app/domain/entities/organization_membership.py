from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from app.domain.value_objects.user_role import UserRole
from app.domain.value_objects.membership_status import MembershipStatus


@dataclass(slots=True)
class OrganizationMembership:
    id: UUID
    org_id: UUID
    user_id: UUID
    role: UserRole = field(default=UserRole.MEMBER)
    status: MembershipStatus = field(default=MembershipStatus.ACTIVE)
    joined_at: datetime | None = None
    invited_by_user_id: UUID | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

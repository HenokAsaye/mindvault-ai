from __future__ import annotations

from dataclasses import dataclass, field
from typing import FrozenSet
from uuid import UUID


@dataclass(frozen=True, slots=True)
class TenantContext:
    org_id: UUID
    user_id: UUID | None = None
    auth_type: str = "jwt"
    roles: FrozenSet[str] = field(default_factory=frozenset)

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import UUID


@dataclass(slots=True)
class User:
    id: UUID
    email: str
    full_name: str
    password_hash: str | None = None
    is_active: bool = True
    is_platform_admin: bool = False
    mfa_enabled: bool = False
    email_verified_at: datetime | None = None
    last_login_at: datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime | None = None
    updated_at: datetime | None = None

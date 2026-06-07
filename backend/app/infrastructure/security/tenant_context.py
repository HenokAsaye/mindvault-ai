from __future__ import annotations

from uuid import UUID

from fastapi import Depends, HTTPException, status

from app.domain.value_objects.tenant_context import TenantContext
from app.infrastructure.security.auth import get_current_claims


def get_tenant_context(claims: dict = Depends(get_current_claims)) -> TenantContext:
    org_id = claims.get("org_id")
    user_id = claims.get("sub")
    role = claims.get("role", "member")
    if not org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Missing org context"
        )

    try:
        parsed_org_id = UUID(str(org_id))
        parsed_user_id = UUID(str(user_id)) if user_id else None
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token claim format",
        ) from exc

    return TenantContext(
        org_id=parsed_org_id,
        user_id=parsed_user_id,
        roles=frozenset({str(role)}),
    )

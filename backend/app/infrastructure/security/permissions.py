from __future__ import annotations

from collections.abc import Callable

from fastapi import Depends, HTTPException, status

from app.infrastructure.security.auth import get_current_claims


def requires_role(*allowed_roles: str) -> Callable:
    allowed = {role.lower() for role in allowed_roles}

    def dependency(claims: dict = Depends(get_current_claims)) -> dict:
        role = str(claims.get("role", "")).lower()
        if role not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions"
            )
        return claims

    return dependency

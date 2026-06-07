from __future__ import annotations

import hashlib
import hmac
import json
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import uuid4

import jwt
from redis.asyncio import Redis

class ThrottleService:
    def __init__(
        self,
        redis: Redis,
        *,
        soft_limit: int,
        hard_limit: int,
        soft_ttl: int,
        hard_ttl: int,
    ) -> None:
        self._redis = redis
        self._soft_limit = soft_limit
        self._hard_limit = hard_limit
        self._soft_ttl = soft_ttl
        self._hard_ttl = hard_ttl

    async def _increment(self, key: str) -> int:
        value = await self._redis.incr(key)
        ttl = await self._redis.ttl(key)
        if ttl == -1:
            await self._redis.expire(key, self._hard_ttl)
        return int(value)

    async def register_login_failure(
        self, *, ip: str, username: str
    ) -> dict[str, int | str]:
        ip_key = f"auth:fail:ip:{ip}"
        user_key = f"auth:fail:user:{username.lower()}"
        ip_count, user_count = await self._increment(ip_key), await self._increment(
            user_key
        )
        severity = "NONE"
        lock_seconds = 0
        count = max(ip_count, user_count)
        if count >= self._hard_limit:
            severity = "HARD_LOCK"
            lock_seconds = self._hard_ttl
        elif count >= self._soft_limit:
            severity = "SOFT_LOCK"
            lock_seconds = self._soft_ttl
        return {"severity": severity, "count": count, "lock_seconds": lock_seconds}

    async def clear_login_failures(self, *, ip: str, username: str) -> None:
        await self._redis.delete(
            f"auth:fail:ip:{ip}", f"auth:fail:user:{username.lower()}"
        )

class TokenService:
    def __init__(
        self,
        redis: Redis,
        *,
        keys: dict[str, str],
        active_kid: str,
        issuer: str,
        audience: str,
    ) -> None:
        self._redis = redis
        self._keys = keys
        self._active_kid = active_kid
        self._issuer = issuer
        self._audience = audience

    def _encode(
        self, *, claims: dict[str, Any], token_type: str, ttl_seconds: int
    ) -> tuple[str, str]:
        now = datetime.now(timezone.utc)
        jti = uuid4().hex
        payload = {
            **claims,
            "jti": jti,
            "type": token_type,
            "iss": self._issuer,
            "aud": self._audience,
            "iat": now,
            "nbf": now,
            "exp": now + timedelta(seconds=ttl_seconds),
        }
        key = self._keys[self._active_kid]
        token = jwt.encode(
            payload, key, algorithm="HS256", headers={"kid": self._active_kid}
        )
        return token, jti

    def decode(self, token: str) -> dict[str, Any]:
        header = jwt.get_unverified_header(token)
        kid = header.get("kid")
        if not kid or kid not in self._keys:
            raise ValueError("Unknown token key")
        return jwt.decode(
            token,
            self._keys[kid],
            algorithms=["HS256"],
            audience=self._audience,
            issuer=self._issuer,
            options={
                "require": ["exp", "iat", "nbf", "iss", "aud", "sub", "jti", "type"]
            },
        )

    async def issue_access(self, *, claims: dict[str, Any], ttl_seconds: int) -> str:
        token, _ = self._encode(
            claims=claims, token_type="access", ttl_seconds=ttl_seconds
        )
        return token

    async def issue_refresh(
        self, *, claims: dict[str, Any], ttl_seconds: int, family_id: str | None = None
    ) -> tuple[str, str, str]:
        token, jti = self._encode(
            claims=claims, token_type="refresh", ttl_seconds=ttl_seconds
        )
        family = family_id or uuid4().hex
        await self._redis.set(
            f"rt:active:{jti}",
            json.dumps({"sub": claims["sub"], "family": family}),
            ex=ttl_seconds,
        )
        return token, jti, family

    async def revoke_access(self, *, jti: str, ttl_seconds: int) -> None:
        await self._redis.set(f"at:blacklist:{jti}", "1", ex=ttl_seconds)

    async def is_access_revoked(self, *, jti: str) -> bool:
        return bool(await self._redis.exists(f"at:blacklist:{jti}"))

    async def rotate_refresh(
        self,
        *,
        presented_jti: str,
        user_id: str,
        org_id: str,
        role: str,
        access_ttl: int,
        refresh_ttl: int,
    ) -> dict[str, str]:
        active_key = f"rt:active:{presented_jti}"
        used_key = f"rt:used:{presented_jti}"
        if await self._redis.exists(used_key):
            await self.revoke_all_for_user(user_id=user_id)
            raise ValueError("Refresh token replay detected")
        payload_raw = await self._redis.get(active_key)
        if not payload_raw:
            await self.revoke_all_for_user(user_id=user_id)
            raise ValueError("Invalid refresh token")
        payload = json.loads(payload_raw)
        await self._redis.set(used_key, "1", ex=refresh_ttl)
        await self._redis.delete(active_key)
        claims = {"sub": user_id, "org_id": org_id, "role": role}
        access = await self.issue_access(claims=claims, ttl_seconds=access_ttl)
        refresh, _, family = await self.issue_refresh(
            claims=claims, ttl_seconds=refresh_ttl, family_id=payload["family"]
        )
        return {"access_token": access, "refresh_token": refresh, "family_id": family}

    async def revoke_all_for_user(self, *, user_id: str) -> None:
        await self._redis.set(
            f"user:sessions:revoked_after:{user_id}",
            int(datetime.now(timezone.utc).timestamp()),
            ex=604800,
        )

    async def is_user_globally_revoked(self, *, user_id: str, iat: int) -> bool:
        cut = await self._redis.get(f"user:sessions:revoked_after:{user_id}")
        return bool(cut and int(iat) <= int(cut))

class InvitationService:
    """Invite token: issuer|invite_id|org_id|email|role|exp|sig."""

    def __init__(self, *, secret: str, issuer: str) -> None:
        self._secret = secret.encode("utf-8")
        self._issuer = issuer

    def issue(
        self,
        *,
        invite_id: str,
        org_id: str,
        email: str,
        role: str,
        expires_in_seconds: int,
    ) -> str:
        exp = int(
            (
                datetime.now(timezone.utc) + timedelta(seconds=expires_in_seconds)
            ).timestamp()
        )
        normalized_email = email.strip().lower()
        normalized_role = role.strip().lower()
        parts = [
            self._issuer,
            invite_id,
            org_id,
            normalized_email,
            normalized_role,
            str(exp),
        ]
        blob = "|".join(parts)
        sig = hmac.new(self._secret, blob.encode("utf-8"), hashlib.sha256).hexdigest()
        return f"{blob}|{sig}"

    def verify(self, token: str) -> dict[str, str]:
        if "|" not in token:
            raise ValueError("Malformed invitation token")
        signed_blob, sig = token.rsplit("|", 1)
        expected_sig = hmac.new(
            self._secret, signed_blob.encode("utf-8"), hashlib.sha256
        ).hexdigest()
        if not hmac.compare_digest(expected_sig, sig):
            raise ValueError("Invalid invitation signature")
        parts = signed_blob.split("|")
        if len(parts) != 6:
            raise ValueError("Malformed invitation token")
        issuer, invite_id, org_id, email, role, exp_str = parts
        if issuer != self._issuer:
            raise ValueError("Invitation issuer mismatch")
        if int(exp_str) < int(datetime.now(timezone.utc).timestamp()):
            raise ValueError("Invitation expired")
        return {"invite_id": invite_id, "org_id": org_id, "email": email, "role": role}

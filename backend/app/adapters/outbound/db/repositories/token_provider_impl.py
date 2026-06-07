from __future__ import annotations
from datetime import datetime, timedelta, timezone

from typing import Any
from uuid import uuid4

import jwt

from app.domain.ports.outbound.token_provider import TokenProvider


class JwtTokenProvider(TokenProvider):
    def __init__(
        self,
        *,
        secret: str,
        algorithm: str = "HS256",
        issuer: str = "mindvault-ai",
        audience: str = "mindvault-clients",
    ) -> None:
        self._secret = secret
        self._algorithm = algorithm
        self._issuer = issuer
        self._audience = audience

    def issue_access_token(
        self, *, claims: dict[str, Any], expires_in_seconds: int
    ) -> str:
        payload = dict(claims)
        now = datetime.now(timezone.utc)
        payload["jti"] = str(uuid4())
        payload["iat"] = now
        payload["nbf"] = now
        payload["exp"] = datetime.now(timezone.utc) + timedelta(
            seconds=expires_in_seconds
        )
        payload["type"] = "access"
        payload["iss"] = self._issuer
        payload["aud"] = self._audience
        return jwt.encode(payload, self._secret, algorithm=self._algorithm)

    def issue_refresh_token(
        self, *, claims: dict[str, Any], expires_in_seconds: int
    ) -> str:
        payload = dict(claims)
        now = datetime.now(timezone.utc)
        payload["jti"] = str(uuid4())
        payload["iat"] = now
        payload["nbf"] = now
        payload["exp"] = datetime.now(timezone.utc) + timedelta(
            seconds=expires_in_seconds
        )
        payload["type"] = "refresh"
        payload["iss"] = self._issuer
        payload["aud"] = self._audience
        return jwt.encode(payload, self._secret, algorithm=self._algorithm)

    def decode_token(self, *, token: str) -> dict[str, Any]:
        try:
            return jwt.decode(
                token,
                self._secret,
                algorithms=[self._algorithm],
                audience=self._audience,
                issuer=self._issuer,
                options={"require": ["exp", "iat", "nbf", "iss", "aud", "sub", "type"]},
            )
        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")
        except jwt.InvalidTokenError:
            raise ValueError("Invalid token")

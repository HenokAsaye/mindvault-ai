"""Unit tests for JWT token provider."""

from __future__ import annotations

import pytest

from app.adapters.outbound.db.repositories.token_provider_impl import JwtTokenProvider


@pytest.mark.unit
class TestJwtTokenProvider:
    @pytest.fixture
    def provider(self) -> JwtTokenProvider:
        return JwtTokenProvider(
            secret="unit-test-secret",
            algorithm="HS256",
            issuer="mindvault-test",
            audience="test-clients",
        )

    def test_issue_and_decode_access_token(self, provider: JwtTokenProvider) -> None:
        claims = {"sub": "user-1", "org_id": "org-1", "role": "owner"}
        token = provider.issue_access_token(claims=claims, expires_in_seconds=3600)
        decoded = provider.decode_token(token=token)
        assert decoded["sub"] == "user-1"
        assert decoded["type"] == "access"

    def test_issue_refresh_token_type(self, provider: JwtTokenProvider) -> None:
        token = provider.issue_refresh_token(
            claims={"sub": "u"}, expires_in_seconds=3600
        )
        decoded = provider.decode_token(token=token)
        assert decoded["type"] == "refresh"

    def test_decode_rejects_garbage(self, provider: JwtTokenProvider) -> None:
        with pytest.raises(ValueError, match="Invalid token"):
            provider.decode_token(token="not.a.jwt")

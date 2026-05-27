from __future__ import annotations

import pytest

from app.adapters.outbound.db.repositories.password_hasher_impl import (
    BcryptPasswordHasher,
)


@pytest.mark.unit
class TestBcryptPasswordHasher:
    def test_hash_and_verify(self) -> None:
        hasher = BcryptPasswordHasher()
        hashed = hasher.hash_password(plain_password="secret-123")
        assert hashed != "secret-123"
        assert hasher.verify_password(
            plain_password="secret-123", hashed_password=hashed
        )

    def test_verify_rejects_wrong_password(self) -> None:
        hasher = BcryptPasswordHasher()
        hashed = hasher.hash_password(plain_password="one")
        assert not hasher.verify_password(plain_password="two", hashed_password=hashed)

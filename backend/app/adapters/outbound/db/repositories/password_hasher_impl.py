from __future__ import annotations

from passlib.context import CryptContext

from app.domain.ports.outbound.password_hasher import PasswordHasher


class BcryptPasswordHasher(PasswordHasher):
    def __init__(self) -> None:
        self._ctx = CryptContext(schemes=["bcrypt_sha256"], deprecated="auto")

    def hash_password(self, *, plain_password: str) -> str:
        return self._ctx.hash(plain_password)

    def verify_password(self, *, plain_password: str, hashed_password: str) -> bool:
        return self._ctx.verify(plain_password, hashed_password)

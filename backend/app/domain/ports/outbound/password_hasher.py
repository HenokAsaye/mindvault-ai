from __future__ import annotations

from abc import ABC, abstractmethod


class PasswordHasher(ABC):
    @abstractmethod
    def hash_password(self, *, plain_password: str) -> str: ...
    @abstractmethod
    def verify_password(self, *, plain_password: str, hashed_password: str) -> bool: ...

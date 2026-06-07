from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any


class TokenProvider(ABC):
    @abstractmethod
    def issue_access_token(
        self, *, claims: dict[str, Any], expires_in_seconds: int
    ) -> str: ...

    @abstractmethod
    def issue_refresh_token(
        self, *, claims: dict[str, Any], expires_in_seconds: int
    ) -> str: ...

    @abstractmethod
    def decode_token(self, *, token: str) -> dict[str, Any]: ...

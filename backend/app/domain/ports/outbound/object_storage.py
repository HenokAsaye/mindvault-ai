from __future__ import annotations
from abc import ABC, abstractmethod


class ObjectStorage(ABC):
    @abstractmethod
    def put_object(
        self, *, key: str, data: bytes, content_type: str | None = None
    ) -> str: ...

    @abstractmethod
    def get_object(self, *, key: str) -> bytes: ...

    @abstractmethod
    def delete_object(self, *, key: str) -> None: ...

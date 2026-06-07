from __future__ import annotations

from abc import ABC, abstractmethod


class DocumentLoader(ABC):
    @abstractmethod
    def supports(self, source_type: str) -> bool: ...

    @abstractmethod
    def load_text(self, *, data: bytes, source_type: str) -> str: ...


class UnsupportedDocumentTypeError(ValueError):
    """Raised when no registered loader supports the given source_type."""


class DocumentLoaderRegistry:
    """Picks a ``DocumentLoader`` for a source_type; first match wins."""

    def __init__(self, loaders: list[DocumentLoader]) -> None:
        self._loaders = list(loaders)

    def load_text(self, *, data: bytes, source_type: str) -> str:
        for loader in self._loaders:
            if loader.supports(source_type):
                return loader.load_text(data=data, source_type=source_type)
        raise UnsupportedDocumentTypeError(
            f"No loader registered for source_type={source_type!r}"
        )

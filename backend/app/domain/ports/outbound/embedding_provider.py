from __future__ import annotations
from abc import ABC, abstractmethod


class EmbeddingProvider(ABC):
    @abstractmethod
    async def embed_text(self, text: str) -> list[float]: ...

    @abstractmethod
    async def embed_texts(self, texts: list[str]) -> list[list[float]]: ...


class SyncEmbeddingProvider(ABC):
    @abstractmethod
    def embed_text(self, text: str) -> list[float]: ...

    @abstractmethod
    def embed_texts(self, texts: list[str]) -> list[list[float]]: ...

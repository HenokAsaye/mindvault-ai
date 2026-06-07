from __future__ import annotations
import asyncio
import logging

from sentence_transformers import SentenceTransformer

from app.domain.ports.outbound.embedding_provider import (
    EmbeddingProvider,
    SyncEmbeddingProvider,
)

logger = logging.getLogger(__name__)


class SyncLocalBGEAdapter(SyncEmbeddingProvider):
    def __init__(self, model_name: str = "BAAI/bge-small-en-v1.5") -> None:
        logger.info("Loading embedding model: %s", model_name)
        self._model = SentenceTransformer(model_name)
        self._model_name = model_name
        logger.info("Embedding model loaded; ready for sync operations")

    def embed_text(self, text: str) -> list[float]:
        if not text or not text.strip():
            logger.debug("Empty text provided for embedding; returning empty vector")
            return []
        embedding = self._model.encode(text, normalize_embeddings=True)
        return embedding.tolist()

    def embed_texts(self, texts: list[str]) -> list[list[float]]:

        if not texts:
            return []
        embeddings = self._model.encode(texts, normalize_embeddings=True)
        return embeddings.tolist()


class AsyncLocalBGEAdapter(EmbeddingProvider):
    def __init__(
        self,
        sync_impl: SyncEmbeddingProvider | None = None,
        model_name: str = "BAAI/bge-small-en-v1.5",
    ) -> None:
        if sync_impl is not None:
            self._sync_impl = sync_impl
            logger.info("Using provided sync embedding implementation")
        else:
            self._sync_impl = SyncLocalBGEAdapter(model_name=model_name)

    async def embed_text(self, text: str) -> list[float]:
        return await asyncio.to_thread(self._sync_impl.embed_text, text)

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return await asyncio.to_thread(self._sync_impl.embed_texts, texts)

"""Dependency injection setup for retrieval policy."""

from __future__ import annotations

from app.adapters.outbound.key.key_retriever import KeyRetriever
from app.adapters.outbound.vector.vector_retriever import VectorRetriever
from app.domain.ports.outbound.full_text_search import FullTextSearch
from app.domain.ports.outbound.reranker import Reranker
from app.domain.ports.outbound.vector_store import VectorStore
from app.domain.ports.outbound.embedding_provider import EmbeddingProvider
from app.domain.services.retrieval_policy import RetrievalPolicy
from app.infrastructure.config.retrieval_config import RetrievalConfig
from app.infrastructure.di import providers


class _KeyRetrieverAdapter:
    def __init__(self, key_retriever: KeyRetriever) -> None:
        self._key_retriever = key_retriever

    async def retrieve(self, query: str, top_k: int = 5, filters=None):
        org_id = (filters or {}).get("org_id")
        if not org_id:
            raise ValueError("filters.org_id is required for keyword retrieval")
        return await self._key_retriever.retrieve_by_keywords(
            query=query,
            org_id=str(org_id),
            top_k=top_k,
        )


def setup_retrieval_dependencies(
    *,
    config: RetrievalConfig | None = None,
    embedder: EmbeddingProvider | None = None,
    vector_store: VectorStore | None = None,
    full_text_search: FullTextSearch | None = None,
    reranker: Reranker | None = None,
) -> RetrievalPolicy:
    """Configure and wire retrieval policy dependencies."""
    config = config or RetrievalConfig()
    embedder = embedder or providers.get_embedder()
    vector_store = vector_store or providers.get_vector_store()
    full_text_search = full_text_search or providers.get_full_text_search()
    reranker = reranker or providers.get_reranker()

    vector_retriever = VectorRetriever(
        embedder=embedder,
        vector_store=vector_store,
    )
    key_retriever = _KeyRetrieverAdapter(KeyRetriever(full_text_search))

    return RetrievalPolicy(
        vector_retriever=vector_retriever,
        key_retriever=key_retriever,
        config=config.to_domain(),
        reranker=reranker,
    )

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Protocol
import logging

from app.domain.value_objects.document import Document
from app.domain.ports.retriever import Retriever
from app.domain.services.result_fusion import fuse_results, apply_reciprocal_rank_fusion


logger = logging.getLogger(__name__)


@dataclass(slots=True, frozen=True)
class RetrievalConfig:

    top_k: int = 5
    retrieve_limit: int = 50
    fusion_weights: Dict[str, float] = field(
        default_factory=lambda: {"vector": 0.6, "key": 0.4}
    )
    normalization_method: str = "softmax"
    fusion_method: str = "weighted"
    rerank_enabled: bool = False
    rerank_top_n: int = 20
    alpha: float = 0.5
    user_reranker: bool = False


Reranker = Protocol  # Placeholder for reranker interface


class RetrievalPolicy:
    def __init__(
        self,
        vector_retriever: Retriever,
        key_retriever: Retriever,
        config: RetrievalConfig,
        reranker: Optional[Reranker] = None,
    ) -> None:
        self.vector_retriever = vector_retriever
        self.key_retriever = key_retriever
        self.config = config
        self.reranker = reranker

        if self.config.top_k <= 0:
            raise ValueError("config.top_k must be > 0")
        if self.config.retrieve_limit <= 0:
            raise ValueError("config.retrieve_limit must be > 0")
        if self.config.fusion_method not in ("weighted", "rrf"):
            raise ValueError(f"Invalid fusion_method: {self.config.fusion_method}")

    async def retrieve(
        self,
        query: str,
        top_k: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None,
        strategy: str = "hybrid",
    ) -> List[Document]:
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")
        if strategy not in ("vector", "key", "hybrid"):
            raise ValueError(
                f"Invalid strategy: {strategy}. Must be 'vector', 'key', or 'hybrid'"
            )

        final_top_k = top_k or self.config.top_k
        if final_top_k <= 0:
            raise ValueError("top_k must be > 0")

        logger.info(
            f"Retrieving with strategy={strategy}, top_k={final_top_k}, "
            f"filters={filters}"
        )

        try:
            if strategy == "vector":
                return await self._retrieve_vector(query, final_top_k, filters)
            elif strategy == "key":
                return await self._retrieve_key(query, final_top_k, filters)
            else:  # hybrid
                return await self._retrieve_hybrid(query, final_top_k, filters)
        except Exception as e:
            logger.error(f"Retrieval failed: {e}", exc_info=True)
            raise

    async def _retrieve_vector(
        self,
        query: str,
        top_k: int,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Document]:
        logger.debug(f"Vector-only retrieval for: {query}")
        results = await self.vector_retriever.retrieve(
            query=query,
            top_k=top_k,
            filters=filters,
        )
        logger.info(f"Vector retrieval returned {len(results)} results")
        return results

    async def _retrieve_key(
        self,
        query: str,
        top_k: int,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Document]:
        logger.debug(f"Keyword-only retrieval for: {query}")
        results = await self.key_retriever.retrieve(
            query=query,
            top_k=top_k,
            filters=filters,
        )
        logger.info(f"Keyword retrieval returned {len(results)} results")
        return results

    async def _retrieve_hybrid(
        self,
        query: str,
        top_k: int,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Document]:
        logger.debug(f"Hybrid retrieval for: {query} (top_k={top_k})")

        intermediate_k = max(self.config.retrieve_limit, top_k * 2)

        try:
            import asyncio

            vector_results, key_results = await asyncio.gather(
                self.vector_retriever.retrieve(
                    query=query,
                    top_k=intermediate_k,
                    filters=filters,
                ),
                self.key_retriever.retrieve(
                    query=query,
                    top_k=intermediate_k,
                    filters=filters,
                ),
                return_exceptions=True,
            )

            if isinstance(vector_results, Exception):
                logger.warning(f"Vector retriever failed: {vector_results}")
                vector_results = []
            if isinstance(key_results, Exception):
                logger.warning(f"Key retriever failed: {key_results}")
                key_results = []

            if not vector_results and not key_results:
                logger.warning("Both retrievers failed or returned empty")
                return []

            logger.info(
                f"Retrieved {len(vector_results)} from vector, "
                f"{len(key_results)} from keyword"
            )

        except Exception as e:
            logger.error(f"Parallel retrieval failed: {e}")
            raise

        if not vector_results:
            logger.info("No vector results; using keyword only")
            fused_results = key_results[:top_k]
        elif not key_results:
            logger.info("No keyword results; using vector only")
            fused_results = vector_results[:top_k]
        else:
            if self.config.fusion_method == "weighted":
                fused_results = fuse_results(
                    vector_results=vector_results,
                    key_results=key_results,
                    fusion_weights=self.config.fusion_weights,
                    top_k=top_k,
                    normalization_method=self.config.normalization_method,
                )
            else:  # rrf
                fused_results = apply_reciprocal_rank_fusion(
                    vector_results=vector_results,
                    key_results=key_results,
                    k=60,
                    top_k=top_k,
                )
            logger.info(f"Fusion produced {len(fused_results)} results")
        if self.config.rerank_enabled and self.reranker:
            rerank_candidates = fused_results[: self.config.rerank_top_n]
            logger.info(f"Reranking top-{len(rerank_candidates)} candidates")

            try:
                reranked = await self.reranker.rerank(
                    query=query,
                    documents=rerank_candidates,
                )
                logger.info("Reranking complete")
                fused_results = reranked + fused_results[self.config.rerank_top_n :]
            except Exception as e:
                logger.warning(f"Reranking failed; using fused results: {e}")

        return fused_results[:top_k]

    async def retrieve_vector_only(
        self,
        query: str,
        top_k: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Document]:
        return await self.retrieve(
            query=query,
            top_k=top_k,
            filters=filters,
            strategy="vector",
        )

    async def retrieve_key_only(
        self,
        query: str,
        top_k: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Document]:
        return await self.retrieve(
            query=query,
            top_k=top_k,
            filters=filters,
            strategy="key",
        )

    async def retrieve_hybrid(
        self,
        query: str,
        top_k: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Document]:
        return await self.retrieve(
            query=query,
            top_k=top_k,
            filters=filters,
            strategy="hybrid",
        )

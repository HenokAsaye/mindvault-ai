from __future__ import annotations

import asyncio
from typing import Dict, List, Optional

from app.domain.ports.outbound.embedding_provider import EmbeddingProvider
from app.domain.ports.outbound.full_text_search import FullTextSearch
from app.domain.ports.outbound.vector_store import VectorStore
from app.domain.services.result_fusion import apply_reciprocal_rank_fusion, fuse_results
from app.domain.value_objects.document import Document


class HybridSearchService:
    def __init__(
        self,
        embedder: EmbeddingProvider,
        vector_store: VectorStore,
        full_text_search: FullTextSearch,
    ) -> None:
        self._embedder = embedder
        self._vector_store = vector_store
        self._full_text_search = full_text_search

    async def search(
        self,
        *,
        user_query: str,
        org_id: str,
        top_k: int = 5,
        fusion_weights: Optional[Dict[str, float]] = None,
        normalization_method: str = "softmax",
        use_rrf: bool = True,
        rrf_k: int = 60,
    ) -> List[Document]:
        fts_task = asyncio.create_task(
            self._full_text_search.search(
                query=user_query,
                org_id=org_id,
                top_k=top_k,
            )
        )

        query_vector = await self._embedder.embed_text(user_query)
        vector_task = asyncio.create_task(
            self._vector_store.query_by_similarity(
                query_vector=query_vector,
                org_id=org_id,
                top_k=top_k,
            )
        )

        vector_matches, key_results = await asyncio.gather(vector_task, fts_task)

        vector_results = []
        for match in vector_matches:
            metadata = match.get("metadata") or {}
            text = (metadata.get("text") or "").strip()
            score = match.get("score")
            doc_id = match.get("id")
            if not doc_id or not text or score is None:
                continue
            if score < 0.0:
                score = 0.0
            elif score > 1.0:
                score = 1.0
            vector_results.append(
                Document(
                    id=doc_id,
                    text=text,
                    score=score,
                    source="vector",
                    metadata=metadata,
                    vector_score=score,
                )
            )

        if use_rrf:
            return apply_reciprocal_rank_fusion(
                vector_results=vector_results,
                key_results=key_results,
                k=rrf_k,
                top_k=top_k,
            )

        return fuse_results(
            vector_results=vector_results,
            key_results=key_results,
            fusion_weights=fusion_weights,
            top_k=top_k,
            normalization_method=normalization_method,
        )

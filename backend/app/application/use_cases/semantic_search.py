from __future__ import annotations

from typing import Any

from app.application.services.hybrid_search_service import HybridSearchService
from app.domain.ports.outbound.reranker import Reranker
from app.domain.services.citation_policy import (
    extract_citations_from_chunks,
    rank_citations,
)
from app.domain.value_objects.document import Document

class SemanticSearchService:
    def __init__(
        self,
        *,
        hybrid_search: HybridSearchService,
        reranker: Reranker,
    ) -> None:
        self._hybrid_search = hybrid_search
        self._reranker = reranker

    async def execute(
        self,
        *,
        org_id: str,
        query: str,
        top_k: int = 5,
    ) -> dict[str, Any]:
        if not query or not query.strip():
            raise ValueError("query must be a non-empty string")

        results = await self._hybrid_search.search(
            user_query=query,
            org_id=org_id,
            top_k=top_k,
        )
        if not results:
            return {"items": [], "citations": [], "total": 0}

        reranked = await self._reranker.rerank(
            query=query,
            documents=results,
            top_k=top_k,
        )

        citations = rank_citations(extract_citations_from_chunks(reranked))
        citation_dicts = [c.__dict__ for c in citations]

        items = [self._to_item(doc) for doc in reranked]
        return {"items": items, "citations": citation_dicts, "total": len(items)}

    def _to_item(self, doc: Document) -> dict[str, Any]:
        metadata = doc.metadata or {}
        citation = {
            "source": metadata.get("file_name", "Unknown"),
            "page_number": metadata.get("page_number"),
            "line_from": metadata.get("line_from"),
            "line_to": metadata.get("line_to"),
            "score": doc.score,
        }
        return {
            "id": doc.id,
            "text": doc.text,
            "score": doc.score,
            "source": doc.source,
            "metadata": metadata,
            "vector_score": doc.vector_score,
            "key_score": doc.key_score,
            "rerank_score": doc.rerank_score,
            "retrieval_sources": doc.retrieval_sources,
            "citation": citation,
        }

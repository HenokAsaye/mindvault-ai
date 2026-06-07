from __future__ import annotations

import asyncio
import logging
from typing import Any
from uuid import UUID

from pinecone import Pinecone

from app.domain.ports.outbound.vector_store import VectorStore

logger = logging.getLogger(__name__)


class PineconeVectorStore(VectorStore):
    def __init__(self, api_key: str, index_name: str) -> None:
        logger.info("Initializing Pinecone vector store with index: %s", index_name)
        self._pc = Pinecone(api_key=api_key)
        self._index = self._pc.Index(index_name)
        self._index_name = index_name
        logger.info("Pinecone vector store initialized")

    async def upsert(
        self, *, vectors: list[dict[str, Any]], namespace: str | None = None
    ) -> None:
        if not vectors:
            logger.debug("No vectors to upsert")
            return

        try:
            await asyncio.to_thread(
                self._index.upsert, vectors=vectors, namespace=namespace
            )
            logger.debug("Upserted %d vectors to Pinecone", len(vectors))
        except Exception:
            logger.exception("Failed to upsert vectors to Pinecone")
            raise

    async def query_by_similarity(
        self,
        *,
        query_vector: list[float],
        org_id: str,
        top_k: int = 5,
        limit: int = 50,
        alpha: float = 0.5,
        user_reranker: bool = True,
        namespace: str | None = None,
    ) -> list[dict[str, Any]]:
        if not query_vector or not len(query_vector):
            logger.warning("Empty query vector provided")
            return []

        try:
            response = await asyncio.to_thread(
                self._index.query,
                vector=query_vector,
                top_k=top_k,
                namespace=namespace,
                filter={"org_id": {"$eq": str(org_id)}},
                include_metadata=True,
            )

            results = []
            for match in response.matches:
                results.append(
                    {
                        "id": match.id,
                        "score": match.score,
                        "metadata": match.metadata or {},
                    }
                )

            logger.debug(
                "Query returned %d matches for org_id=%s", len(results), org_id
            )
            return results
        except Exception:
            logger.exception("Failed to query vector store")
            raise

    async def delete_by_document_id(
        self, *, document_id: UUID | str, org_id: UUID | str
    ) -> None:
        try:
            response = await asyncio.to_thread(
                self._index.query,
                vector=[0.0] * 1536,
                top_k=10000,
                namespace=None,
                filter={
                    "org_id": {"$eq": str(org_id)},
                    "document_id": {"$eq": str(document_id)},
                },
                include_metadata=True,
            )

            ids_to_delete = [match.id for match in response.matches]

            if ids_to_delete:
                await asyncio.to_thread(
                    self._index.delete, ids=ids_to_delete, namespace=None
                )
                logger.info(
                    "Deleted %d vectors for document_id=%s, org_id=%s",
                    len(ids_to_delete),
                    document_id,
                    org_id,
                )
            else:
                logger.debug(
                    "No vectors found to delete for document_id=%s, org_id=%s",
                    document_id,
                    org_id,
                )
        except Exception:
            logger.exception("Failed to delete vectors for document_id=%s", document_id)
            raise

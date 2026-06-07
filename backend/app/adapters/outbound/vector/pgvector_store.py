from __future__ import annotations

import json
import logging
from typing import Any
from uuid import UUID

import sqlalchemy as sa

from app.domain.ports.outbound.vector_store import VectorStore

logger = logging.getLogger(__name__)

class PGVectorStore(VectorStore):
    def __init__(self, engine: Any) -> None:
        self._engine = engine
        logger.info("PGVector store initialized")

    async def _ensure_table_exists(self) -> None:
        async with self._engine.begin() as conn:
            await conn.execute(sa.text("CREATE EXTENSION IF NOT EXISTS vector"))
            await conn.execute(sa.text("""
                    CREATE TABLE IF NOT EXISTS vectors (
                        id TEXT PRIMARY KEY,
                        org_id TEXT NOT NULL,
                        document_id TEXT NOT NULL,
                        namespace TEXT,
                        embedding vector(1536) NOT NULL,
                        metadata JSONB,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    """))
            logger.debug("Ensured vectors table exists")

    async def upsert(
        self, *, vectors: list[dict[str, Any]], namespace: str | None = None
    ) -> None:
        if not vectors:
            logger.debug("No vectors to upsert")
            return

        await self._ensure_table_exists()

        async with self._engine.begin() as conn:
            for vector in vectors:
                vector_id = vector.get("id")
                values = vector.get("values", [])
                metadata = vector.get("metadata", {})

                org_id = metadata.get("org_id")
                document_id_val = metadata.get("document_id")

                if not vector_id or not values or not org_id:
                    logger.warning(
                        "Skipping invalid vector: missing id, values, or org_id"
                    )
                    continue

                embedding_str = f"[{','.join(str(v) for v in values)}]"

                stmt = sa.text("""
                    INSERT INTO vectors
                        (id, org_id, document_id, namespace, embedding, metadata)
                    VALUES
                        (:id, :org_id, :document_id, :namespace, :embedding, :metadata)
                    ON CONFLICT (id) DO UPDATE SET
                        embedding = EXCLUDED.embedding,
                        metadata = EXCLUDED.metadata
                    """)

                await conn.execute(
                    stmt,
                    {
                        "id": vector_id,
                        "org_id": org_id,
                        "document_id": document_id_val,
                        "namespace": namespace,
                        "embedding": embedding_str,
                        "metadata": json.dumps(metadata),
                    },
                )

        logger.debug("Upserted %d vectors to pgvector", len(vectors))

    async def query_by_similarity(
        self,
        *,
        query_vector: list[float],
        org_id: UUID | str,
        top_k: int = 5,
        namespace: str | None = None,
    ) -> list[dict[str, Any]]:
        if not query_vector or not len(query_vector):
            logger.warning("Empty query vector provided")
            return []

        await self._ensure_table_exists()

        query_embedding = f"[{','.join(str(v) for v in query_vector)}]"

        async with self._engine.begin() as conn:
            where_clause = "WHERE org_id = :org_id"
            if namespace:
                where_clause += " AND namespace = :namespace"

            stmt = sa.text(("""
                    SELECT
                        id,
                        1 - (embedding <=> :embedding::vector) AS score,
                        metadata
                    FROM vectors
                    {where_clause}
                    ORDER BY embedding <=> :embedding::vector
                    LIMIT :top_k
                    """).format(where_clause=where_clause))

            params = {
                "embedding": query_embedding,
                "org_id": str(org_id),
                "top_k": top_k,
            }
            if namespace:
                params["namespace"] = namespace

            result = await conn.execute(stmt, params)
            rows = result.fetchall()

            results = []
            for row in rows:
                results.append(
                    {
                        "id": row[0],
                        "score": float(row[1]),
                        "metadata": json.loads(row[2]) if row[2] else {},
                    }
                )

            logger.debug(
                "Query returned %d matches for org_id=%s", len(results), org_id
            )
            return results

    async def delete_by_document_id(
        self, *, document_id: UUID | str, org_id: UUID | str
    ) -> None:
        await self._ensure_table_exists()

        async with self._engine.begin() as conn:
            stmt = sa.text("""
                DELETE FROM vectors
                WHERE document_id = :document_id AND org_id = :org_id
            """)

            result = await conn.execute(
                stmt, {"document_id": str(document_id), "org_id": str(org_id)}
            )

            deleted_count = result.rowcount
            logger.info(
                "Deleted %d vectors for document_id=%s, org_id=%s",
                deleted_count,
                document_id,
                org_id,
            )

class SyncPGVectorStore:
    def __init__(self, engine: Any) -> None:
        self._engine = engine
        logger.info("Sync PGVector store initialized")

    def _ensure_table_exists(self) -> None:
        with self._engine.begin() as conn:
            conn.execute(sa.text("CREATE EXTENSION IF NOT EXISTS vector"))
            conn.execute(sa.text("""
                    CREATE TABLE IF NOT EXISTS vectors (
                        id TEXT PRIMARY KEY,
                        org_id TEXT NOT NULL,
                        document_id TEXT NOT NULL,
                        namespace TEXT,
                        embedding vector(1536) NOT NULL,
                        metadata JSONB,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    """))

    def upsert(
        self, *, vectors: list[dict[str, Any]], namespace: str | None = None
    ) -> None:
        if not vectors:
            logger.debug("No vectors to upsert")
            return

        self._ensure_table_exists()

        with self._engine.begin() as conn:
            for vector in vectors:
                vector_id = vector.get("id")
                values = vector.get("values", [])
                metadata = vector.get("metadata", {})

                org_id = metadata.get("org_id")
                document_id_val = metadata.get("document_id")

                if not vector_id or not values or not org_id:
                    logger.warning("Skipping invalid vector")
                    continue

                embedding_str = f"[{','.join(str(v) for v in values)}]"

                stmt = sa.text("""
                    INSERT INTO vectors
                        (id, org_id, document_id, namespace, embedding, metadata)
                    VALUES
                        (:id, :org_id, :document_id, :namespace, :embedding, :metadata)
                    ON CONFLICT (id) DO UPDATE SET
                        embedding = EXCLUDED.embedding,
                        metadata = EXCLUDED.metadata
                    """)

                conn.execute(
                    stmt,
                    {
                        "id": vector_id,
                        "org_id": org_id,
                        "document_id": document_id_val,
                        "namespace": namespace,
                        "embedding": embedding_str,
                        "metadata": json.dumps(metadata),
                    },
                )

        logger.debug("Upserted %d vectors to pgvector", len(vectors))

    def delete_by_document_id(
        self, *, document_id: UUID | str, org_id: UUID | str
    ) -> None:
        self._ensure_table_exists()

        with self._engine.begin() as conn:
            stmt = sa.text("""
                DELETE FROM vectors
                WHERE document_id = :document_id AND org_id = :org_id
                """)

            result = conn.execute(
                stmt, {"document_id": str(document_id), "org_id": str(org_id)}
            )

            logger.info(
                "Deleted %d vectors for document_id=%s, org_id=%s",
                result.rowcount,
                document_id,
                org_id,
            )

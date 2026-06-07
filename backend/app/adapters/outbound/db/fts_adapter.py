from sqlalchemy import text as sa_text
from app.domain.ports.outbound.full_text_search import FullTextSearch
from app.domain.value_objects.document import Document


class FTSAdapter(FullTextSearch):
    def __init__(self, *, session_factory) -> None:
        self._session_factory = session_factory

    async def search(
        self, *, query: str, org_id: str, top_k: int = 5
    ) -> list[Document]:
        ts_query = sa_text("""
            SELECT
                dc.id,
                dc.content AS text,
                ts_rank_cd(dc.__ts_vector__, plainto_tsquery('english', :query))
                AS score,
                'key' as source,
                dc.metadata_json as metadata
            FROM
                document_chunks dc
            WHERE
                dc.org_id = :org_id AND
                dc.__ts_vector__ @@ plainto_tsquery('english', :query)
            ORDER BY
                score DESC
            LIMIT :top_k;
            """)

        async with self._session_factory() as session:
            result = await session.execute(
                ts_query, {"query": query, "org_id": org_id, "top_k": top_k}
            )

            docs = []
            for row in result.fetchall():
                content_text = (row.text or "").strip()
                if not content_text:
                    continue
                score = row.score or 0.0
                if score < 0.0:
                    score = 0.0
                elif score > 1.0:
                    score = 1.0
                docs.append(
                    Document(
                        id=row.id,
                        text=content_text,
                        score=score,
                        source=row.source,
                        metadata=row.metadata,
                    )
                )

            return docs

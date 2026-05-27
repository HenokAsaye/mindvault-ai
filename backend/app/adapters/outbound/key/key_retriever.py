from typing import List
from app.domain.ports.outbound.full_text_search import FullTextSearch
from app.domain.value_objects.document import Document


class KeyRetriever:
    def __init__(self, fts_adapter: FullTextSearch):
        self._fts_adapter = fts_adapter

    async def retrieve_by_keywords(
        self, *, query: str, org_id: str, top_k: int = 5
    ) -> List[Document]:
        return await self._fts_adapter.search(query=query, org_id=org_id, top_k=top_k)

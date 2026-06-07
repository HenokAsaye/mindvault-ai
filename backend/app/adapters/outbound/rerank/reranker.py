from app.domain.ports.outbound.reranker import Reranker
from app.domain.value_objects.document import Document

class NoOpReranker(Reranker):

    async def rerank(
        self, *, query: str, documents: list[Document], top_k: int = 5
    ) -> list[Document]:
        return documents[:top_k]

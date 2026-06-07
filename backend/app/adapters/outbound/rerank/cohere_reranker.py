from typing import List
import cohere
from app.domain.ports.outbound.reranker import Reranker
from app.domain.value_objects.document import Document


class CohereReranker(Reranker):
    def __init__(self, api_key: str):
        self.client = cohere.AsyncClient(api_key)

    async def rerank(
        self, *, query: str, documents: List[Document], top_k: int = 5
    ) -> List[Document]:

        response = await self.client.rerank(
            query=query,
            documents=[doc.text for doc in documents],
            top_n=top_k,
            model="rerank-english-v2.0",
        )

        reranked_docs = []
        for r in response.results:
            doc = documents[r.index]

            reranked_doc = Document(
                id=doc.id,
                text=doc.text,
                score=r.relevance_score,
                source="reranked",
                metadata=doc.metadata,
                vector_score=doc.vector_score,
                key_score=doc.key_score,
                rerank_score=r.relevance_score,
            )
            reranked_docs.append(reranked_doc)

        return reranked_docs

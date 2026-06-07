from abc import ABC, abstractmethod
from typing import List
from app.domain.value_objects.document import Document

class Reranker(ABC):
    @abstractmethod
    async def rerank(
        self, *, query: str, documents: List[Document], top_k: int = 5
    ) -> List[Document]:
        raise NotImplementedError

from abc import ABC, abstractmethod
from typing import List
from app.domain.value_objects.document import Document


class FullTextSearch(ABC):
    @abstractmethod
    async def search(
        self, *, query: str, org_id: str, top_k: int = 5
    ) -> List[Document]:
        raise NotImplementedError

from typing import List, Dict, Any, Optional, Protocol, runtime_checkable
from app.domain.value_objects.document import Document


@runtime_checkable
class Retriever(Protocol):

    async def retrieve(
        self,
        query: str,
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Document]: ...

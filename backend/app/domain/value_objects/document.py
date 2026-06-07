from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class Document:
    id: str
    text: str
    score: float
    source: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    vector_score: Optional[float] = None
    key_score: Optional[float] = None
    rerank_score: Optional[float] = None
    retrieval_sources: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.id or not self.id.strip():
            raise ValueError("Document id cannot be empty")
        if not self.text or not self.text.strip():
            raise ValueError("Document text cannot be empty")
        if not (0.0 <= self.score <= 1.0):
            raise ValueError(f"Document score must be in [0.0, 1.0], got {self.score}")
        if self.source not in ("vector", "key", "hybrid", "reranked"):
            raise ValueError(f"Invalid source: {self.source}")

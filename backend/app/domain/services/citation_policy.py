from typing import List, Dict, Any, Optional
from app.domain.value_objects.document import Document

class Citation:

    def __init__(
        self,
        source: str,
        page_number: Optional[int] = None,
        line_from: Optional[int] = None,
        line_to: Optional[int] = None,
        score: float = 0.0,
    ):
        self.source = source
        self.page_number = page_number
        self.line_from = line_from
        self.line_to = line_to
        self.score = score

    def __repr__(self) -> str:
        return (
            f"Citation(source={self.source}, page={self.page_number}, "
            f"lines=({self.line_from}-{self.line_to}), score={self.score:.4f})"
        )

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Citation):
            return NotImplemented
        return (
            self.source == other.source
            and self.page_number == other.page_number
            and self.line_from == other.line_from
            and self.line_to == other.line_to
        )

    def __hash__(self) -> int:
        return hash((self.source, self.page_number, self.line_from, self.line_to))

def extract_citations_from_chunks(chunks: List[Document]) -> List[Citation]:
    citations: Dict[int, Citation] = {}

    for chunk in chunks:
        metadata = chunk.metadata or {}
        source = metadata.get("file_name", "Unknown")
        page_number = metadata.get("page_number")
        line_from = metadata.get("line_from")
        line_to = metadata.get("line_to")

        citation = Citation(
            source=source,
            page_number=page_number,
            line_from=line_from,
            line_to=line_to,
            score=chunk.score,
        )

        if page_number is not None:
            if (
                page_number not in citations
                or citation.score > citations[page_number].score
            ):
                citations[page_number] = citation
        else:
            citations[hash(citation)] = citation

    return list(citations.values())

def rank_citations(citations: List[Citation]) -> List[Citation]:
    return sorted(citations, key=lambda c: c.score, reverse=True)

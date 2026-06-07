from __future__ import annotations

from app.domain.ports.outbound.document_loader import DocumentLoader

_TEXT_TYPES = {"text", "txt", "text/plain"}
_MD_TYPES = {"markdown", "md", "text/markdown"}
_SUPPORTED = _TEXT_TYPES | _MD_TYPES

class TextDocumentLoader(DocumentLoader):
    def supports(self, source_type: str) -> bool:
        return (source_type or "").lower() in _SUPPORTED

    def load_text(self, *, data: bytes, source_type: str) -> str:
        return data.decode("utf-8", errors="replace")

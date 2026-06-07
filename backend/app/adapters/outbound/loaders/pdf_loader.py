from __future__ import annotations

import io
import logging

from pypdf import PdfReader
from pypdf.errors import PdfReadError, PdfStreamError

from app.domain.ports.outbound.document_loader import DocumentLoader

logger = logging.getLogger(__name__)

_SUPPORTED = {"pdf", "application/pdf"}


class PDFDocumentLoader(DocumentLoader):
    def supports(self, source_type: str) -> bool:
        return (source_type or "").lower() in _SUPPORTED

    def load_text(self, *, data: bytes, source_type: str) -> str:
        if not data:
            return ""
        try:
            reader = PdfReader(io.BytesIO(data))
        except (PdfReadError, PdfStreamError, OSError) as exc:
            raise ValueError(f"Invalid or corrupted PDF: {exc}") from exc

        if reader.is_encrypted:
            try:
                if reader.decrypt("") == 0:
                    logger.warning(
                        "Encrypted PDF could not be decrypted with empty password"
                    )
                    return ""
            except Exception:
                logger.exception("Failed to decrypt PDF")
                return ""

        pages: list[str] = []
        for page_number, page in enumerate(reader.pages, start=1):
            try:
                text = page.extract_text() or ""
            except Exception:
                logger.exception("Failed to extract text from PDF page %d", page_number)
                text = ""
            if text:
                pages.append(text)
        return "\n\f\n".join(pages)

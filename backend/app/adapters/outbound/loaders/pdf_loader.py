"""PDF document loader.

Uses ``pypdf`` (pure Python, MIT-licensed) to extract page text. Pages are
joined with a form-feed separator so downstream chunkers can recover page
boundaries if needed.

Edge cases:
  * Encrypted PDFs without a password yield empty text rather than raising.
  * Non-PDF bytes raise ``ValueError`` with a clear message instead of
    bubbling pypdf's internal errors to the worker.
"""

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
                # pypdf returns 0 if decryption fails or 1/2 on success.
                if reader.decrypt("") == 0:
                    logger.warning(
                        "Encrypted PDF could not be decrypted with empty password"
                    )
                    return ""
            except Exception:  # noqa: BLE001 — decryption can raise broadly
                logger.exception("Failed to decrypt PDF")
                return ""

        pages: list[str] = []
        for page_number, page in enumerate(reader.pages, start=1):
            try:
                text = page.extract_text() or ""
            except Exception:  # noqa: BLE001 — keep going past poison pages
                logger.exception("Failed to extract text from PDF page %d", page_number)
                text = ""
            if text:
                pages.append(text)
        # Form-feed (\f) is the conventional page separator; chunker treats it
        # as whitespace.
        return "\n\f\n".join(pages)

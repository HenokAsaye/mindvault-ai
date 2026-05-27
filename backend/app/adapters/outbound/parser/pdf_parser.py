from __future__ import annotations

import io
import logging
from typing import BinaryIO

import fitz

logger = logging.getLogger(__name__)


class PDFParser:
    def extract_text(self, file_stream: BinaryIO) -> str:
        try:
            data = file_stream.read()
            if not data:
                return ""

            doc = fitz.open(stream=io.BytesIO(data), filetype="pdf")
        except Exception as exc:
            logger.exception("Invalid or corrupted PDF file")
            raise ValueError(f"Invalid or corrupted PDF: {exc}") from exc

        pages: list[str] = []

        for page_num, page in enumerate(doc, start=1):
            try:
                text = page.get_text() or ""
                if text:
                    pages.append(text)
            except Exception:
                logger.exception("Failed to extract text from PDF page %d", page_num)
                continue

        return "\n\f\n".join(pages) if pages else ""

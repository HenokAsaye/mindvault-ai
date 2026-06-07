from __future__ import annotations

import logging
from typing import BinaryIO
from pathlib import Path

from app.adapters.outbound.parser.pdf_parser import PDFParser
from app.adapters.outbound.parser.doc_parser import DocxParser
from app.adapters.outbound.parser.text_parser import TextParser, MarkdownParser

logger = logging.getLogger(__name__)


class ParserFactory:
    def __init__(self):
        self._pdf_parser = PDFParser()
        self._docx_parser = DocxParser()
        self._text_parser = TextParser()
        self._markdown_parser = MarkdownParser()

        self._extension_map = {
            ".pdf": self._pdf_parser,
            ".docx": self._docx_parser,
            ".doc": self._docx_parser,
            ".txt": self._text_parser,
            ".text": self._text_parser,
        }

    def extract_text(self, file_stream: BinaryIO, file_path: str) -> str:
        extension = Path(file_path).suffix.lower()

        if extension not in self._extension_map:
            raise ValueError(
                f"Unsupported file type: {extension}. "
                f"Supported types: {', '.join(self._extension_map.keys())}"
            )

        parser = self._extension_map[extension]
        logger.info(f"Using {parser.__class__.__name__} for file: {file_path}")

        return parser.extract_text(file_stream)

    def get_supported_extensions(self) -> list[str]:
        return list(self._extension_map.keys())

    def is_supported(self, file_path: str) -> bool:
        extension = Path(file_path).suffix.lower()
        return extension in self._extension_map

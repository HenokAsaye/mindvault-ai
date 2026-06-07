from __future__ import annotations
import io
import logging
from typing import BinaryIO

from docx import Document as DocxDocument
from docx.opc.exceptions import PackageNotFoundError
from docx.oxml.ns import qn

logger = logging.getLogger(__name__)


class DocxParser:
    def extract_text(self, file_stream: BinaryIO) -> str:
        try:
            data = file_stream.read()
            if not data:
                return ""

            doc = DocxDocument(io.BytesIO(data))
        except PackageNotFoundError as exc:
            logger.exception("Invalid or corrupted DOCX file")
            raise ValueError("Invalid or corrupted DOCX file") from exc
        except Exception as exc:
            logger.exception("Failed to parse DOCX file")
            raise ValueError(f"Failed to parse DOCX file: {exc}") from exc

        parts: list[str] = []
        body = doc.element.body
        for child in body.iterchildren():
            tag = child.tag
            if tag == qn("w:p"):
                text = self._extract_paragraph_text(child)
                if text:
                    parts.append(text)
            elif tag == qn("w:tbl"):
                table_text = self._extract_table_text(child)
                if table_text:
                    parts.append(table_text)
        return "\n\n".join(parts) if parts else ""

    @staticmethod
    def _extract_paragraph_text(p_element) -> str:
        runs: list[str] = []
        for t in p_element.iter(qn("w:t")):
            if t.text:
                runs.append(t.text)
        return "".join(runs).strip()

    @staticmethod
    def _extract_table_text(tbl_element) -> str:
        rows: list[str] = []

        for row in tbl_element.iter(qn("w:tr")):
            cells: list[str] = []

            for cell in row.iter(qn("w:tc")):
                cell_paragraphs = [
                    DocxParser._extract_paragraph_text(p) for p in cell.iter(qn("w:p"))
                ]
                cell_text = " ".join(p for p in cell_paragraphs if p).strip()
                if cell_text:
                    cells.append(cell_text)

            if cells:
                rows.append(" | ".join(cells))

        return "\n".join(rows) if rows else ""

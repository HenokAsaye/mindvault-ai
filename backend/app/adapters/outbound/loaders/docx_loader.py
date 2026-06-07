from __future__ import annotations

import io
import logging

from docx import Document as DocxDocument
from docx.opc.exceptions import PackageNotFoundError
from docx.oxml.ns import qn

from app.domain.ports.outbound.document_loader import DocumentLoader

logger = logging.getLogger(__name__)

_SUPPORTED = {
    "docx",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}


class DocxDocumentLoader(DocumentLoader):
    def supports(self, source_type: str) -> bool:
        return (source_type or "").lower() in _SUPPORTED

    def load_text(self, *, data: bytes, source_type: str) -> str:
        if not data:
            return ""
        try:
            doc = DocxDocument(io.BytesIO(data))
        except PackageNotFoundError as exc:
            raise ValueError("Invalid or corrupted DOCX file") from exc

        parts: list[str] = []
        body = doc.element.body
        for child in body.iterchildren():
            tag = child.tag
            if tag == qn("w:p"):
                text = _paragraph_text(child)
                if text:
                    parts.append(text)
            elif tag == qn("w:tbl"):
                rows = _table_rows(child)
                if rows:
                    parts.append("\n".join(rows))
        return "\n\n".join(parts)


def _paragraph_text(p_element) -> str:
    runs: list[str] = []
    for t in p_element.iter(qn("w:t")):
        if t.text:
            runs.append(t.text)
    return "".join(runs).strip()


def _table_rows(tbl_element) -> list[str]:
    rows: list[str] = []
    for row in tbl_element.iter(qn("w:tr")):
        cells: list[str] = []
        for cell in row.iter(qn("w:tc")):
            cell_paragraphs = [_paragraph_text(p) for p in cell.iter(qn("w:p"))]
            cell_text = " ".join(p for p in cell_paragraphs if p).strip()
            if cell_text:
                cells.append(cell_text)
        if cells:
            rows.append(" | ".join(cells))
    return rows

"""Unit tests for document source type inference."""

from __future__ import annotations

import pytest

from app.adapters.inbound.api.v1.routes_documents import _infer_source_type

@pytest.mark.unit
class TestInferSourceType:
    def test_from_pdf_content_type(self) -> None:
        assert _infer_source_type(None, "application/pdf") == "pdf"

    def test_from_docx_content_type(self) -> None:
        ct = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        assert _infer_source_type(None, ct) == "docx"

    def test_from_filename_extension(self) -> None:
        assert _infer_source_type("readme.md", None) == "markdown"
        assert _infer_source_type("notes.txt", None) == "text"
        assert _infer_source_type("paper.pdf", None) == "pdf"

    def test_defaults_to_text(self) -> None:
        assert _infer_source_type("unknown", None) == "text"

"""Unit tests for text/markdown document loaders."""

from __future__ import annotations

import pytest

from app.adapters.outbound.loaders.text_loader import TextDocumentLoader

@pytest.mark.unit
class TestTextDocumentLoader:
    def test_supports_text_and_markdown_types(self) -> None:
        loader = TextDocumentLoader()
        assert loader.supports("text")
        assert loader.supports("markdown")
        assert loader.supports("text/plain")
        assert not loader.supports("pdf")

    def test_load_text_decodes_utf8(self) -> None:
        loader = TextDocumentLoader()
        assert loader.load_text(data="café".encode(), source_type="text") == "café"

    def test_load_text_replaces_invalid_bytes(self) -> None:
        loader = TextDocumentLoader()
        result = loader.load_text(data=b"\xff\xfe", source_type="txt")
        assert isinstance(result, str)

"""Unit tests for parser factory."""

from __future__ import annotations

from io import BytesIO

import pytest

from app.adapters.outbound.parser.parser_factory import ParserFactory
from app.adapters.outbound.parser.text_parser import TextParser


@pytest.mark.unit
class TestParserFactory:
    def test_extracts_plain_text(self) -> None:
        factory = ParserFactory()
        stream = BytesIO(b"Hello from txt")
        text = factory.extract_text(stream, "notes.txt")
        assert "Hello" in text

    def test_unsupported_extension_raises(self) -> None:
        factory = ParserFactory()
        with pytest.raises(ValueError, match="Unsupported file type"):
            factory.extract_text(BytesIO(b"x"), "file.xyz")

    def test_is_supported(self) -> None:
        factory = ParserFactory()
        assert factory.is_supported("doc.pdf")
        assert not factory.is_supported("archive.zip")


@pytest.mark.unit
class TestTextParser:
    def test_extract_text(self) -> None:
        parser = TextParser()
        assert parser.extract_text(BytesIO(b"line")) == "line"

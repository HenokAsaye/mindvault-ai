"""Unit tests for document loader registry."""

from __future__ import annotations

import pytest

from app.adapters.outbound.loaders.text_loader import TextDocumentLoader
from app.domain.ports.outbound.document_loader import (
    DocumentLoaderRegistry,
    UnsupportedDocumentTypeError,
)


@pytest.mark.unit
def test_registry_loads_text() -> None:
    registry = DocumentLoaderRegistry([TextDocumentLoader()])
    text = registry.load_text(data=b"hello", source_type="text")
    assert text == "hello"


@pytest.mark.unit
def test_registry_raises_for_unknown_type() -> None:
    registry = DocumentLoaderRegistry([TextDocumentLoader()])
    with pytest.raises(UnsupportedDocumentTypeError):
        registry.load_text(data=b"x", source_type="application/unknown")

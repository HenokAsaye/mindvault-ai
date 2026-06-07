"""Unit tests for domain exceptions."""

from __future__ import annotations

import pytest

from app.domain.exceptions import (
    DocumentEmptyError,
    DocumentTooLargeError,
    DomainError,
    UnsupportedSourceTypeError,
)

@pytest.mark.unit
def test_domain_errors_inherit_from_base() -> None:
    assert issubclass(DocumentEmptyError, DomainError)
    assert issubclass(DocumentTooLargeError, DomainError)
    assert issubclass(UnsupportedSourceTypeError, DomainError)

@pytest.mark.unit
def test_document_empty_error_message() -> None:
    err = DocumentEmptyError("empty file")
    assert str(err) == "empty file"

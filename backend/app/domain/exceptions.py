from __future__ import annotations

class DomainError(Exception):
    pass

class DocumentEmptyError(DomainError):
    pass

class DocumentTooLargeError(DomainError):
    pass

class UnsupportedSourceTypeError(DomainError):
    pass

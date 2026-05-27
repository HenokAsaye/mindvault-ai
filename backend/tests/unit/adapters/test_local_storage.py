"""Unit tests for local filesystem object storage."""

from __future__ import annotations

import pytest

from app.adapters.outbound.storage.local_storage import LocalObjectStorage


@pytest.mark.unit
class TestLocalObjectStorage:
    def test_put_and_get_roundtrip(self, storage_dir) -> None:
        storage = LocalObjectStorage(base_dir=storage_dir)
        key = "org-id/doc-id/file.txt"
        storage.put_object(key=key, data=b"payload", content_type="text/plain")
        assert storage.get_object(key=key) == b"payload"

    def test_delete_is_idempotent(self, storage_dir) -> None:
        storage = LocalObjectStorage(base_dir=storage_dir)
        key = "a/b.txt"
        storage.put_object(key=key, data=b"x")
        storage.delete_object(key=key)
        storage.delete_object(key=key)

    def test_rejects_path_traversal(self, storage_dir) -> None:
        storage = LocalObjectStorage(base_dir=storage_dir)
        with pytest.raises(ValueError, match="escapes"):
            storage.put_object(key="../../etc/passwd", data=b"x")

    def test_rejects_empty_key(self, storage_dir) -> None:
        storage = LocalObjectStorage(base_dir=storage_dir)
        with pytest.raises(ValueError):
            storage.put_object(key="", data=b"x")

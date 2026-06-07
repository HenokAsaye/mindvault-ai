"""Contract tests: LocalObjectStorage satisfies ObjectStorage port semantics."""

from __future__ import annotations

import pytest

from app.adapters.outbound.storage.local_storage import LocalObjectStorage

@pytest.mark.contract
class TestObjectStorageContract:
    """Behaviors required by all ObjectStorage implementations."""

    @pytest.fixture
    def storage(self, storage_dir) -> LocalObjectStorage:
        return LocalObjectStorage(base_dir=storage_dir)

    def test_put_returns_key(self, storage: LocalObjectStorage) -> None:
        key = storage.put_object(key="a/b", data=b"1")
        assert key == "a/b"

    def test_get_after_put(self, storage: LocalObjectStorage) -> None:
        storage.put_object(key="doc", data=b"bytes")
        assert storage.get_object(key="doc") == b"bytes"

    def test_delete_removes_object(self, storage: LocalObjectStorage) -> None:
        storage.put_object(key="rm", data=b"x")
        storage.delete_object(key="rm")
        with pytest.raises(FileNotFoundError):
            storage.get_object(key="rm")

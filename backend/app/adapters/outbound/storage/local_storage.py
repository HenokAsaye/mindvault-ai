from __future__ import annotations

import os
import stat
import tempfile
from pathlib import Path

from app.domain.ports.outbound.object_storage import ObjectStorage

FILE_MODE = 0o644
DIR_MODE = 0o755

class LocalObjectStorage(ObjectStorage):
    def __init__(self, *, base_dir: str | Path) -> None:
        self._base_dir = Path(base_dir).resolve()
        self._base_dir.mkdir(parents=True, exist_ok=True)
        _ensure_mode(self._base_dir, DIR_MODE)

    def _resolve(self, key: str) -> Path:
        if not key or key.startswith("/"):
            raise ValueError("Storage key must be a non-empty, relative path")
        path = (self._base_dir / key).resolve()
        if self._base_dir not in path.parents and path != self._base_dir:
            raise ValueError("Storage key escapes base dir")
        return path

    def put_object(
        self, *, key: str, data: bytes, content_type: str | None = None
    ) -> str:
        target = self._resolve(key)
        target.parent.mkdir(parents=True, exist_ok=True)
        for parent in _parents_below(target.parent, self._base_dir):
            _ensure_mode(parent, DIR_MODE)
        fd, tmp_path = tempfile.mkstemp(prefix=".tmp-", dir=str(target.parent))
        try:
            with os.fdopen(fd, "wb") as fh:
                fh.write(data)
                fh.flush()
                os.fsync(fh.fileno())
            os.chmod(tmp_path, FILE_MODE)
            os.replace(tmp_path, target)
        except Exception:
            try:
                os.unlink(tmp_path)
            except FileNotFoundError:
                pass
            raise
        return key

    def get_object(self, *, key: str) -> bytes:
        return self._resolve(key).read_bytes()

    def delete_object(self, *, key: str) -> None:
        try:
            self._resolve(key).unlink()
        except FileNotFoundError:
            return

def _parents_below(start: Path, base: Path) -> list[Path]:
    """Return ``[base, ..., start]`` if start is under base else ``[start]``."""
    try:
        rel = start.resolve().relative_to(base)
    except ValueError:
        return [start]
    chain: list[Path] = [base]
    cur = base
    for part in rel.parts:
        cur = cur / part
        chain.append(cur)
    return chain

def _ensure_mode(path: Path, mode: int) -> None:
    """Best-effort chmod; ignore if we don't own the file (e.g. existing dir)."""
    try:
        current = stat.S_IMODE(path.stat().st_mode)
        if current != mode:
            os.chmod(path, mode)
    except (PermissionError, FileNotFoundError):
        return

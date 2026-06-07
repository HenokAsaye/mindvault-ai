from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class ChunkingConfig:
    chunk_size_chars: int = 1500
    chunk_overlap_chars: int = 200

    def __post_init__(self) -> None:
        if self.chunk_size_chars <= 0:
            raise ValueError("chunk_size_chars must be > 0")
        if (
            self.chunk_overlap_chars < 0
            or self.chunk_overlap_chars >= self.chunk_size_chars
        ):
            raise ValueError("chunk_overlap_chars must be in [0, chunk_size_chars)")


def chunk_text(text: str, *, config: ChunkingConfig) -> list[str]:
    normalized = (text or "").strip()
    if not normalized:
        return []

    size = config.chunk_size_chars
    overlap = config.chunk_overlap_chars
    chunks: list[str] = []
    start = 0
    n = len(normalized)
    while start < n:
        end = min(start + size, n)
        if end < n:
            window = normalized[start:end]
            split = _find_safe_break(window)
            if split > 0:
                end = start + split
        chunk = normalized[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end == n:
            break
        start = max(end - overlap, start + 1)
    return chunks


def _find_safe_break(window: str) -> int:
    paragraph = window.rfind("\n\n")
    if paragraph > len(window) * 0.5:
        return paragraph + 2
    newline = window.rfind("\n")
    if newline > len(window) * 0.5:
        return newline + 1
    for marker in (". ", "? ", "! "):
        sentence = window.rfind(marker)
        if sentence > len(window) * 0.5:
            return sentence + len(marker)
    return 0


def estimate_token_count(text: str) -> int:
    if not text:
        return 0
    return max(1, (len(text) + 3) // 4)

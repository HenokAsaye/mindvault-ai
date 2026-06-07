"""Unit tests for document chunking domain policy."""

from __future__ import annotations

import pytest

from app.domain.services.chunking_policy import (
    ChunkingConfig,
    chunk_text,
    estimate_token_count,
)

@pytest.mark.unit
class TestChunkingConfig:
    def test_valid_defaults(self) -> None:
        cfg = ChunkingConfig()
        assert cfg.chunk_size_chars == 1500
        assert cfg.chunk_overlap_chars == 200

    def test_rejects_zero_chunk_size(self) -> None:
        with pytest.raises(ValueError, match="chunk_size_chars"):
            ChunkingConfig(chunk_size_chars=0)

    def test_rejects_overlap_ge_size(self) -> None:
        with pytest.raises(ValueError, match="chunk_overlap"):
            ChunkingConfig(chunk_size_chars=100, chunk_overlap_chars=100)

@pytest.mark.unit
class TestChunkText:
    def test_empty_returns_empty_list(self) -> None:
        assert chunk_text("", config=ChunkingConfig()) == []
        assert chunk_text("   \n  ", config=ChunkingConfig()) == []

    def test_short_text_single_chunk(self) -> None:
        text = "Short document body."
        chunks = chunk_text(text, config=ChunkingConfig(chunk_size_chars=500))
        assert chunks == [text]

    def test_splits_on_paragraph_boundary(self) -> None:
        para1 = "A" * 400
        para2 = "B" * 400
        text = f"{para1}\n\n{para2}"
        cfg = ChunkingConfig(chunk_size_chars=500, chunk_overlap_chars=50)
        chunks = chunk_text(text, config=cfg)
        assert len(chunks) >= 2
        assert all(c.strip() for c in chunks)

    def test_overlap_produces_multiple_chunks(self) -> None:
        text = "word " * 300
        cfg = ChunkingConfig(chunk_size_chars=80, chunk_overlap_chars=20)
        chunks = chunk_text(text, config=cfg)
        assert len(chunks) > 1

@pytest.mark.unit
class TestEstimateTokenCount:
    def test_empty_is_zero(self) -> None:
        assert estimate_token_count("") == 0

    def test_non_empty_at_least_one(self) -> None:
        assert estimate_token_count("hi") >= 1

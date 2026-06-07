from __future__ import annotations

from typing import BinaryIO

class TextParser:
    def extract_text(self, file_stream: BinaryIO) -> str:
        data = file_stream.read()
        return data.decode("utf-8", errors="replace")

class MarkdownParser:
    def extract_text(self, file_stream: BinaryIO) -> str:
        data = file_stream.read()
        return data.decode("utf-8", errors="replace")

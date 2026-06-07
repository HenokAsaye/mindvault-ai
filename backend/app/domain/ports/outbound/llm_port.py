from __future__ import annotations

from abc import ABC, abstractmethod
from typing import AsyncGenerator

class LLMPort(ABC):
    @abstractmethod
    async def generate_response_stream(
        self,
        *,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
    ) -> AsyncGenerator[str, None]: ...

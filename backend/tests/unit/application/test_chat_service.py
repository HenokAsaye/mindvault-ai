"""Unit tests for RAG chat application service."""

from __future__ import annotations

from uuid import uuid4

import pytest

from app.application.services.chat_service import ChatService
from app.domain.value_objects.document import Document
from tests.helpers.mocks import FakeUoW

class FakeHybridSearch:
    async def search(self, **kwargs) -> list[Document]:
        return [
            Document(
                id="doc-1",
                text="context snippet",
                score=0.8,
                source="hybrid",
                metadata={"document_id": "doc-1", "title": "Doc"},
            )
        ]

class FakeReranker:
    async def rerank(self, **kwargs) -> list[Document]:
        return kwargs["documents"]

class FakeLLM:
    async def generate_response_stream(self, *, messages, temperature=0.7):
        yield "Hello "
        yield "world"

class FakeMessageRepo:
    async def get_recent_by_session(self, session_id, limit=6):
        return []

    async def add_message(self, message):
        self.last = message

class FakeSessionRepo:
    async def get_chat_session(self, session_id):
        class Session:
            last_message_at = None

        return Session()

    async def update_chat_session(self, session):
        pass

class FakeSessionUoW(FakeUoW):
    def __init__(self) -> None:
        super().__init__()
        self.messages = FakeMessageRepo()
        self.sessions = FakeSessionRepo()

@pytest.mark.unit
@pytest.mark.asyncio
async def test_chat_service_streams_llm_tokens() -> None:
    uow = FakeSessionUoW()
    service = ChatService(
        hybrid_search=FakeHybridSearch(),
        reranker=FakeReranker(),
        llm=FakeLLM(),
        uow_factory=lambda: uow,
    )
    chunks = []
    async for part in service.ask_question(
        session_id=uuid4(),
        org_id=uuid4(),
        user_id=uuid4(),
        user_query="What is MindVault?",
    ):
        chunks.append(part)
    assert "".join(chunks) == "Hello world"
    assert uow.committed

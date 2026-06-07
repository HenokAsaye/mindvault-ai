"""Integration tests for chat streaming API."""

from __future__ import annotations

from uuid import uuid4

import pytest

from app.infrastructure.di.container import Container
from app.main import app

@pytest.mark.integration
def test_chat_streams_plain_text(authed_client) -> None:
    class FakeChatService:
        async def ask_question(self, **kwargs):
            yield "chunk-1"
            yield "chunk-2"

    app.dependency_overrides[Container.get_chat_service] = lambda: FakeChatService()
    session_id = uuid4()
    response = authed_client.post(
        f"/api/v1/chats/{session_id}/ask",
        json={"message": "Hello?"},
        headers={"Authorization": "Bearer x"},
    )
    app.dependency_overrides.pop(Container.get_chat_service, None)
    assert response.status_code == 200
    assert response.text == "chunk-1chunk-2"

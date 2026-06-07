from __future__ import annotations

import logging
from datetime import datetime
from typing import AsyncGenerator
from uuid import UUID

from app.application.services.hybrid_search_service import HybridSearchService
from app.domain.entities.chat_message import ChatMessage
from app.domain.ports.outbound.llm_port import LLMPort
from app.domain.ports.outbound.reranker import Reranker
from app.domain.ports.outbound.unit_of_work import UnitOfWork
from app.domain.services.citation_policy import (
    extract_citations_from_chunks,
    rank_citations,
)
from app.infrastructure.prompts.loader import SYSTEM_PROMPT_TEMPLATE

logger = logging.getLogger(__name__)

class ChatService:
    def __init__(
        self,
        hybrid_search: HybridSearchService,
        reranker: Reranker,
        llm: LLMPort,
        uow_factory: type,
    ) -> None:
        self._hybrid_search = hybrid_search
        self._reranker = reranker
        self._llm = llm
        self._uow_factory = uow_factory

    async def ask_question(
        self,
        *,
        session_id: UUID,
        org_id: UUID,
        user_id: UUID,
        user_query: str,
    ) -> AsyncGenerator[str, None]:
        context_matches = await self._hybrid_search.search(
            user_query=user_query,
            org_id=str(org_id),
            top_k=5,
        )

        context_chunks = await self._reranker.rerank(
            query=user_query,
            documents=context_matches,
            top_k=5,
        )

        context_text = "\n".join(chunk.text for chunk in context_chunks)
        citations = rank_citations(extract_citations_from_chunks(context_chunks))
        citations_as_dicts = [c.__dict__ for c in citations]

        async with self._uow_factory() as uow:
            uow: UnitOfWork
            history = await uow.messages.get_recent_by_session(session_id, limit=6)

            user_msg = ChatMessage.create_user_message(
                session_id=session_id,
                org_id=org_id,
                user_id=user_id,
                content=user_query,
            )
            await uow.messages.add_message(user_msg)
            await uow.commit()

        messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT_TEMPLATE.format(context=context_text),
            },
            *[{"role": m.role, "content": m.content} for m in history],
            {"role": "user", "content": user_query},
        ]

        full_response = ""
        async for chunk in self._llm.generate_response_stream(messages=messages):
            full_response += chunk
            yield chunk

        async with self._uow_factory() as uow:
            uow: UnitOfWork
            ai_msg = ChatMessage.create_assistant_message(
                session_id=session_id,
                org_id=org_id,
                user_id=user_id,
                content=full_response,
                citations=citations_as_dicts,
                model_id=None,
            )
            await uow.messages.add_message(ai_msg)

            session = await uow.sessions.get_chat_session(session_id)
            session.last_message_at = datetime.now()
            await uow.sessions.update_chat_session(session)
            await uow.commit()

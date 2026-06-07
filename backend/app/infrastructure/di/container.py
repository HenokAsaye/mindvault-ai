from __future__ import annotations

from dataclasses import dataclass

from app.infrastructure.di import providers

@dataclass(slots=True)
class Container:
    get_register_user_service = staticmethod(providers.get_register_user_service)
    get_login_user_service = staticmethod(providers.get_login_user_service)
    get_switch_org_service = staticmethod(providers.get_switch_org_service)
    get_iam_service = staticmethod(providers.get_iam_service)
    get_object_storage = staticmethod(providers.get_object_storage)
    get_document_repository = staticmethod(providers.get_document_repository)
    get_chunk_repository = staticmethod(providers.get_chunk_repository)
    get_ingest_document_service = staticmethod(providers.get_ingest_document_service)
    get_process_document_chunks_service = staticmethod(
        providers.get_process_document_chunks_service
    )
    get_embedder = staticmethod(providers.get_embedder)
    get_vector_store = staticmethod(providers.get_vector_store)
    get_chat_service = staticmethod(providers.get_chat_service)
    get_semantic_search_service = staticmethod(providers.get_semantic_search_service)

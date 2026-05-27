from __future__ import annotations

from fastapi import FastAPI

from app.adapters.inbound.api.v1 import (
    routes_auth,
    routes_chat,
    routes_documents,
    routes_search,
)
from app.infrastructure import celery_app  # noqa: F401

app = FastAPI(
    title="MindVault AI Backend",
    description="Multi-tenant RAG SaaS backend APIs",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.include_router(routes_auth.router, prefix="/api/v1")
app.include_router(routes_documents.router, prefix="/api/v1")
app.include_router(routes_chat.router, prefix="/api/v1")
app.include_router(routes_search.router, prefix="/api/v1")


@app.get("/health", tags=["system"])
async def health() -> dict[str, str]:
    return {"status": "ok"}

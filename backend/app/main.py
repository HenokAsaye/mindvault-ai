from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.cors import CORSMiddleware

from app.adapters.inbound.api.v1 import (
    routes_auth,
    routes_chat,
    routes_documents,
    routes_search,
)
from app.infrastructure import celery_app

app = FastAPI(
    title="MindVault AI Backend",
    description="Multi-tenant RAG SaaS backend APIs",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes_auth.router, prefix="/api/v1")
app.include_router(routes_documents.router, prefix="/api/v1")
app.include_router(routes_chat.router, prefix="/api/v1")
app.include_router(routes_search.router, prefix="/api/v1")

@app.get("/health", tags=["system"])
async def health() -> dict[str, str]:
    return {"status": "ok"}

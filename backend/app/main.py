from __future__ import annotations

import app.infrastructure.celery_app

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.adapters.inbound.api.v1 import routes_auth, routes_chat, routes_documents

app = FastAPI(
    title="MindVault AI Backend",
    description="Multi-tenant RAG SaaS backend APIs",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Enable CORS for frontend development
# In production, replace with your actual domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",      # Next.js frontend dev server
        "http://127.0.0.1:3000",
        "http://localhost:3001",      # Alternative port
        "http://127.0.0.1:3001",
    ],
    allow_credentials=True,            # Allow cookies/credentials
    allow_methods=["*"],               # Allow all HTTP methods
    allow_headers=["*"],               # Allow all headers (Content-Type, Authorization, etc)
)

app.include_router(routes_auth.router, prefix="/api/v1")
app.include_router(routes_documents.router, prefix="/api/v1")
app.include_router(routes_chat.router, prefix="/api/v1")


@app.get("/health", tags=["system"])
async def health() -> dict[str, str]:
    return {"status": "ok"}

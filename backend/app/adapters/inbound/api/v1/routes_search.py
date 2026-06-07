from __future__ import annotations

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.application.dto.requests import SearchRequest
from app.application.dto.responses import SearchResponse
from app.infrastructure.di.container import Container
from app.infrastructure.security.auth import get_current_claims

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/search", tags=["search"])


@router.post("", response_model=SearchResponse)
async def search(
    payload: SearchRequest,
    claims: dict = Depends(get_current_claims),
    search_service=Depends(Container.get_semantic_search_service),
) -> SearchResponse:
    org_id = UUID(claims["org_id"])
    try:
        result = await search_service.execute(
            org_id=str(org_id),
            query=payload.query,
            top_k=payload.top_k,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except Exception:
        logger.exception("Semantic search failed")
        raise

    return SearchResponse(**result)

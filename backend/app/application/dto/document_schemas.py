from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, StrictInt, StrictStr

class DocumentResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    id: str
    org_id: str
    title: str
    source_type: str
    status: str
    chunk_count: int
    token_count: int
    checksum: str | None = None
    error_message: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

class DocumentListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    items: list[DocumentResponse]
    total: int
    page: int
    page_size: int

class DocumentChunkResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    id: str
    chunk_index: int
    content: str
    content_hash: str
    token_count_estimate: int

class DocumentChunksResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    document_id: str
    items: list[DocumentChunkResponse]
    total: int

class DocumentListQuery(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    page: StrictInt = Field(default=1, ge=1)
    page_size: StrictInt = Field(default=20, ge=1, le=100)
    status: StrictStr | None = Field(
        default=None, pattern="^(pending|processing|ready|failed)$"
    )

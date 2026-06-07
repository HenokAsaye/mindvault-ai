from __future__ import annotations

import os
from collections.abc import Iterator
from pathlib import Path
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient

@pytest.fixture(scope="session")
def app_instance():
    os.environ.setdefault("ENVIRONMENT", "development")
    os.environ.setdefault("JWT_SECRET", "test-jwt-secret-for-unit-tests-only")
    os.environ.setdefault("JWT_KEYS", "k1:test-jwt-secret-for-unit-tests-only")
    os.environ.setdefault("JWT_ACTIVE_KID", "k1")
    os.environ.setdefault("REDIS_URL", "redis://localhost:6379/15")
    os.environ.setdefault(
        "DATABASE_URL",
        "postgresql+asyncpg://postgres:postgres@localhost:5432/mindvault_test",
    )
    os.environ.setdefault("DOCUMENT_STORAGE_DIR", "/tmp/mindvault-test-storage")
    os.environ.setdefault("PINECONE_API_KEY", "")
    os.environ.setdefault("OPENAI_API_KEY", "")

    from app.main import app

    return app

@pytest.fixture
def test_org_id() -> UUID:
    return uuid4()

@pytest.fixture
def test_user_id() -> UUID:
    return uuid4()

@pytest.fixture
def auth_claims(test_user_id: UUID, test_org_id: UUID) -> dict:
    return {
        "sub": str(test_user_id),
        "org_id": str(test_org_id),
        "role": "owner",
        "jti": str(uuid4()),
        "iat": 1_700_000_000,
        "type": "access",
    }

@pytest.fixture
def api_client(app_instance) -> Iterator[TestClient]:
    with TestClient(app_instance) as client:
        yield client

@pytest.fixture
def authed_client(
    api_client: TestClient, auth_claims: dict, app_instance
) -> Iterator[TestClient]:
    from app.infrastructure.security.auth import get_current_claims

    async def _override() -> dict:
        return auth_claims

    app_instance.dependency_overrides[get_current_claims] = _override
    yield api_client
    app_instance.dependency_overrides.pop(get_current_claims, None)

@pytest.fixture
def storage_dir(tmp_path: Path) -> Path:
    path = tmp_path / "object-storage"
    path.mkdir()
    os.environ["DOCUMENT_STORAGE_DIR"] = str(path)
    return path

@pytest.fixture(autouse=True)
def _clear_dependency_overrides(app_instance) -> Iterator[None]:
    yield
    app_instance.dependency_overrides.clear()

@pytest.fixture
def sample_text_bytes() -> bytes:
    return b"Hello MindVault.\n\nThis is a test document for chunking."

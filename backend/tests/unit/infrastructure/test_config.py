"""Unit tests for application settings."""

from __future__ import annotations

import importlib

import pytest

def _reload_settings_module(monkeypatch: pytest.MonkeyPatch, **env: str) -> object:
    for key, value in env.items():
        monkeypatch.setenv(key, value)
    import app.infrastructure.config as config_module

    return importlib.reload(config_module)

@pytest.mark.unit
def test_settings_jwt_keys_parsing(monkeypatch: pytest.MonkeyPatch) -> None:
    config_module = _reload_settings_module(
        monkeypatch,
        JWT_KEYS="k1:secret-one,k2:secret-two",
        JWT_ACTIVE_KID="k1",
        ENVIRONMENT="development",
    )
    s = config_module.Settings()
    assert s.jwt_keys["k1"] == "secret-one"
    assert s.jwt_keys["k2"] == "secret-two"

@pytest.mark.unit
def test_document_allowed_source_types_normalized(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config_module = _reload_settings_module(
        monkeypatch,
        DOCUMENT_ALLOWED_SOURCE_TYPES=" PDF , text ",
        JWT_ACTIVE_KID="k1",
        JWT_KEYS="k1:test-key",
        ENVIRONMENT="development",
    )
    s = config_module.Settings()
    assert "pdf" in s.document_allowed_source_types
    assert "text" in s.document_allowed_source_types

@pytest.mark.unit
def test_production_jwt_validation_fails_with_dev_secret(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    with pytest.raises(RuntimeError, match="JWT_SECRET"):
        _reload_settings_module(
            monkeypatch,
            ENVIRONMENT="production",
            JWT_SECRET="dev-secret",
            JWT_ACTIVE_KID="k1",
            JWT_KEYS="k1:dev-secret",
        )
    _reload_settings_module(
        monkeypatch,
        ENVIRONMENT="development",
        JWT_SECRET="test-jwt-secret-for-unit-tests-only",
        JWT_ACTIVE_KID="k1",
        JWT_KEYS="k1:test-jwt-secret-for-unit-tests-only",
    )

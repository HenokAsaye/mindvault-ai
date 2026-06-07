from __future__ import annotations

import os


class Settings:
    environment: str = os.getenv("ENVIRONMENT", "development")
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://postgres:postgres@localhost:5432/mindvault",
    )
    jwt_secret: str = os.getenv("JWT_SECRET", "dev-secret")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    jwt_issuer: str = os.getenv("JWT_ISSUER", "mindvault-ai")
    jwt_audience: str = os.getenv("JWT_AUDIENCE", "mindvault-clients")
    access_token_ttl_seconds: int = int(os.getenv("ACCESS_TOKEN_TTL_SECONDS", "3600"))
    refresh_token_ttl_seconds: int = int(
        os.getenv("REFRESH_TOKEN_TTL_SECONDS", "604800")
    )
    mfa_attempt_ttl_seconds: int = int(os.getenv("MFA_ATTEMPT_TTL_SECONDS", "300"))
    invitation_ttl_seconds: int = int(os.getenv("INVITATION_TTL_SECONDS", "172800"))
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    jwt_active_kid: str = os.getenv("JWT_ACTIVE_KID", "k1")
    jwt_keys_raw: str = os.getenv("JWT_KEYS", "k1:dev-secret")
    login_soft_lock_threshold: int = int(os.getenv("LOGIN_SOFT_LOCK_THRESHOLD", "5"))
    login_hard_lock_threshold: int = int(os.getenv("LOGIN_HARD_LOCK_THRESHOLD", "10"))
    login_soft_lock_seconds: int = int(os.getenv("LOGIN_SOFT_LOCK_SECONDS", "900"))
    login_hard_lock_seconds: int = int(os.getenv("LOGIN_HARD_LOCK_SECONDS", "86400"))
    invitation_signing_secret: str = os.getenv("INVITATION_SIGNING_SECRET", "").strip()
    frontend_base_url: str = os.getenv(
        "FRONTEND_BASE_URL", "http://localhost:5173"
    ).rstrip("/")
    celery_broker_url: str = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/1")
    celery_result_backend: str = os.getenv(
        "CELERY_RESULT_BACKEND", "redis://localhost:6379/2"
    )
    celery_task_default_queue: str = os.getenv("CELERY_TASK_DEFAULT_QUEUE", "default")
    celery_email_queue: str = os.getenv("CELERY_EMAIL_QUEUE", "default")
    celery_timezone: str = os.getenv("CELERY_TIMEZONE", "UTC")

    document_storage_dir: str = os.getenv("DOCUMENT_STORAGE_DIR", "/app/var/storage")
    document_max_size_bytes: int = int(
        os.getenv("DOCUMENT_MAX_SIZE_BYTES", str(25 * 1024 * 1024))
    )
    document_chunk_size_chars: int = int(os.getenv("DOCUMENT_CHUNK_SIZE_CHARS", "1500"))
    document_chunk_overlap_chars: int = int(
        os.getenv("DOCUMENT_CHUNK_OVERLAP_CHARS", "200")
    )
    document_allowed_source_types_raw: str = os.getenv(
        "DOCUMENT_ALLOWED_SOURCE_TYPES",
        ",".join(
            [
                "text",
                "markdown",
                "txt",
                "md",
                "text/plain",
                "text/markdown",
                "pdf",
                "application/pdf",
                "docx",
                "application/vnd.openxmlformats-officedocument"
                ".wordprocessingml.document",
            ]
        ),
    )

    pinecone_api_key: str = os.getenv("PINECONE_API_KEY", "")
    pinecone_index_name: str = os.getenv("PINECONE_INDEX_NAME", "mindvault")

    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    cohere_api_key: str = os.getenv("COHERE_API_KEY", "")

    @property
    def document_allowed_source_types(self) -> set[str]:
        return {
            t.strip().lower()
            for t in self.document_allowed_source_types_raw.split(",")
            if t.strip()
        }

    def validate(self) -> None:
        if self.environment.lower() in {"prod", "production"}:
            if self.jwt_secret == "dev-secret" or len(self.jwt_secret) < 32:
                raise RuntimeError(
                    "JWT_SECRET must be set with at least 32 characters in production."
                )
        if self.jwt_active_kid not in self.jwt_keys:
            raise RuntimeError("JWT_ACTIVE_KID must exist in JWT_KEYS.")

    @property
    def jwt_keys(self) -> dict[str, str]:
        pairs: dict[str, str] = {}
        for item in self.jwt_keys_raw.split(","):
            if ":" not in item:
                continue
            kid, key = item.split(":", 1)
            pairs[kid.strip()] = key.strip()
        if not pairs:
            pairs["k1"] = self.jwt_secret
        return pairs

    @property
    def smtp_enabled(self) -> bool:
        return os.getenv("SMTP_ENABLED", "false").lower() in {"true", "1", "yes"}

    @property
    def smtp_host(self) -> str:
        return os.getenv("SMTP_HOST", "").strip()

    @property
    def smtp_port(self) -> int:
        return int(os.getenv("SMTP_PORT", "587"))

    @property
    def smtp_username(self) -> str:
        return (os.getenv("SMTP_USERNAME", "") or "").strip()

    @property
    def smtp_password(self) -> str:
        raw = (os.getenv("SMTP_PASSWORD", "") or "").strip()
        if len(raw) >= 2 and raw[0] == raw[-1] and raw[0] in {'"', "'"}:
            raw = raw[1:-1].strip()
        return raw

    @property
    def smtp_use_tls(self) -> bool:
        return os.getenv("SMTP_USE_TLS", "true").lower() in {"true", "1", "yes"}

    @property
    def smtp_from_email(self) -> str:
        return os.getenv("SMTP_FROM_EMAIL", "").strip()

    @property
    def smtp_from_name(self) -> str:
        return (os.getenv("SMTP_FROM_NAME", "") or "").strip() or "MindVault AI"

    @property
    def smtp_password_for_auth(self) -> str:
        """Gmail app passwords are 16 chars; SMTP auth strips spaces."""
        return "".join((self.smtp_password or "").split())

    @property
    def use_smtp_email_delivery(self) -> bool:
        """Whether to use real SMTP (vs NullEmailSender).

        Requires host + from address. Also requires either ``SMTP_ENABLED=true``
        or a non-empty ``SMTP_PASSWORD`` so a common misconfiguration (credentials
        set but flag left false) still sends mail.
        """
        if not self.smtp_host or not self.smtp_from_email:
            return False
        if self.smtp_enabled:
            return True
        return bool(self.smtp_password_for_auth)


settings = Settings()
settings.validate()

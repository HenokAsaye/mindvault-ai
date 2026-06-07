"""Email-related Celery tasks.

The API enqueues work with ``.delay()`` / ``apply_async()``; this module runs in
a **worker** process. It builds the real ``EmailSender`` from env (same as the
API) so SMTP / MJML configuration is identical.

Uses ``shared_task`` so this module does not import ``celery_app`` directly
(circular import safe).
"""

from __future__ import annotations

import logging

from celery import shared_task

from app.adapters.outbound.email.email_sender import NullEmailSender
from app.infrastructure.config import settings

logger = logging.getLogger(__name__)

TASK_NAME = "mindvault.email.send_organization_invitation"

@shared_task(
    name=TASK_NAME,
    bind=True,
    autoretry_for=(OSError, ConnectionError),
    retry_backoff=10,
    retry_kwargs={"max_retries": 3},
)
def send_organization_invitation_email(
    self,
    *,
    to_email: str,
    invite_url: str,
    org_name: str,
    role: str,
    expires_in_hours: int,
) -> None:
    """Render MJML (or simple HTML fallback) + send SMTP for a single org invitation."""
    from app.infrastructure.di.providers import get_email_sender

    sender = get_email_sender()
    if isinstance(sender, NullEmailSender):
        logger.warning(
            "Invitation email to %s was not sent: SMTP disabled or incomplete config. "
            "Set SMTP_HOST, SMTP_FROM_EMAIL, and either SMTP_ENABLED=true or "
            "SMTP_PASSWORD. "
            "current: host=%r from=%r enabled=%s has_password=%s",
            to_email,
            settings.smtp_host,
            settings.smtp_from_email,
            settings.smtp_enabled,
            bool(settings.smtp_password_for_auth),
        )
        return

    logger.info(
        "Sending invitation email to %s via SMTP host %s", to_email, settings.smtp_host
    )
    try:
        sender.send_invitation_email(
            to_email=to_email,
            invite_url=invite_url,
            org_name=org_name,
            role=role,
            expires_in_hours=expires_in_hours,
        )
    except Exception:
        logger.exception("Unexpected failure sending invitation email to %s", to_email)
        raise

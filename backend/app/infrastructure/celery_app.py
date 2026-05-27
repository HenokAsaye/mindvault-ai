from __future__ import annotations

from celery import Celery

from app.infrastructure.config import settings
from app.application.tasks import audit_tasks, document_tasks, email_tasks  # noqa: F401

celery_app = Celery(
    "mindvault",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone=settings.celery_timezone,
    enable_utc=True,
    task_default_queue=settings.celery_task_default_queue,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_track_started=True,
    broker_connection_retry_on_startup=True,
)

if (
    settings.celery_email_queue
    and settings.celery_email_queue != settings.celery_task_default_queue
):
    celery_app.conf.task_routes = {
        "mindvault.email.send_organization_invitation": {
            "queue": settings.celery_email_queue
        },
    }

__all__ = ["celery_app"]

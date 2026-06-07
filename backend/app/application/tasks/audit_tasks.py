from __future__ import annotations

import logging
from typing import Any
from uuid import UUID, uuid4

from celery import shared_task

from app.adapters.outbound.db.celery_worker_db import worker_session
from app.adapters.outbound.db.sqlalchemy_models import AuditLogORM

logger = logging.getLogger(__name__)

TASK_NAME = "mindvault.audit.record_event"


def _persist_audit_sync(
    *,
    event_type: str,
    actor_id: str | None,
    org_id: str | None,
    target_user_id: str | None,
    ip_address: str | None,
    user_agent: str | None,
    metadata: dict[str, Any],
) -> None:
    session = worker_session()
    try:
        session.add(
            AuditLogORM(
                id=uuid4(),
                event_type=event_type,
                actor_id=UUID(actor_id) if actor_id else None,
                org_id=UUID(org_id) if org_id else None,
                target_user_id=UUID(target_user_id) if target_user_id else None,
                ip_address=ip_address,
                user_agent=user_agent,
                metadata_json=metadata,
            )
        )
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


@shared_task(name=TASK_NAME, bind=True)
def record_audit_event(
    self,
    *,
    event_type: str,
    actor_id: str | None = None,
    org_id: str | None = None,
    target_user_id: str | None = None,
    ip_address: str | None = None,
    user_agent: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> None:
    try:
        _persist_audit_sync(
            event_type=event_type,
            actor_id=actor_id,
            org_id=org_id,
            target_user_id=target_user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata=metadata or {},
        )
    except Exception:
        logger.exception("Failed to persist audit event %s", event_type)
        raise

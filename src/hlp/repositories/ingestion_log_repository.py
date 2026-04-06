"""IngestionLog data access."""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from hlp.models.ingestion_log import IngestionLog
from hlp.shared.exceptions import NotFoundError


def list_paginated(
    db: Session,
    page: int = 1,
    size: int = 25,
    agent_type: str | None = None,
    status: str | None = None,
) -> tuple[list[IngestionLog], int]:
    base = select(IngestionLog)
    if agent_type is not None:
        base = base.where(IngestionLog.agent_type == agent_type)
    if status is not None:
        base = base.where(IngestionLog.status == status)

    total = db.execute(select(func.count()).select_from(base.subquery())).scalar_one()
    stmt = (
        base.order_by(IngestionLog.run_timestamp.desc())
        .offset((page - 1) * size)
        .limit(size)
    )
    items = list(db.execute(stmt).scalars().all())
    return items, int(total)


def get(db: Session, log_id: int) -> IngestionLog | None:
    return db.get(IngestionLog, log_id)


def get_or_raise(db: Session, log_id: int) -> IngestionLog:
    obj = get(db, log_id)
    if obj is None:
        raise NotFoundError(f"Ingestion log {log_id} not found")
    return obj

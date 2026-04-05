"""StatusHistory data access."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from hlp.models.status_history import StatusHistory


def list_by_lot(db: Session, lot_id: int) -> list[StatusHistory]:
    stmt = (
        select(StatusHistory)
        .where(StatusHistory.lot_id == lot_id)
        .order_by(StatusHistory.changed_at.desc())
    )
    return list(db.execute(stmt).scalars().all())


def create(db: Session, **fields) -> StatusHistory:
    record = StatusHistory(**fields)
    db.add(record)
    db.flush()
    return record

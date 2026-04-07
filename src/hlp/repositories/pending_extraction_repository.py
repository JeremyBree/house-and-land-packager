"""PendingExtraction data access."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from hlp.models.pending_extraction import PendingExtraction
from hlp.shared.exceptions import NotFoundError


def list_pending(
    db: Session, status: str | None = None
) -> list[PendingExtraction]:
    stmt = select(PendingExtraction).order_by(PendingExtraction.created_at.desc())
    if status:
        stmt = stmt.where(PendingExtraction.status == status)
    return list(db.execute(stmt).scalars().all())


def get(db: Session, extraction_id: int) -> PendingExtraction | None:
    return db.get(PendingExtraction, extraction_id)


def create(db: Session, **fields) -> PendingExtraction:
    obj = PendingExtraction(**fields)
    db.add(obj)
    db.flush()
    return obj


def update(db: Session, extraction_id: int, **fields) -> PendingExtraction:
    obj = get(db, extraction_id)
    if obj is None:
        raise NotFoundError(f"PendingExtraction {extraction_id} not found")
    for k, v in fields.items():
        setattr(obj, k, v)
    db.flush()
    return obj


def delete(db: Session, extraction_id: int) -> None:
    obj = get(db, extraction_id)
    if obj is None:
        raise NotFoundError(f"PendingExtraction {extraction_id} not found")
    db.delete(obj)
    db.flush()

"""EstateDocument data access."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from hlp.models.estate_document import EstateDocument
from hlp.shared.exceptions import DocumentNotFoundError


def list_by_estate(db: Session, estate_id: int) -> list[EstateDocument]:
    stmt = (
        select(EstateDocument)
        .where(EstateDocument.estate_id == estate_id)
        .order_by(EstateDocument.created_at.desc())
    )
    return list(db.execute(stmt).scalars().all())


def list_by_stage(db: Session, stage_id: int) -> list[EstateDocument]:
    stmt = (
        select(EstateDocument)
        .where(EstateDocument.stage_id == stage_id)
        .order_by(EstateDocument.created_at.desc())
    )
    return list(db.execute(stmt).scalars().all())


def get(db: Session, document_id: int) -> EstateDocument | None:
    return db.get(EstateDocument, document_id)


def create(db: Session, **fields) -> EstateDocument:
    doc = EstateDocument(**fields)
    db.add(doc)
    db.flush()
    return doc


def delete(db: Session, document_id: int) -> None:
    doc = get(db, document_id)
    if doc is None:
        raise DocumentNotFoundError(f"Document {document_id} not found")
    db.delete(doc)
    db.flush()

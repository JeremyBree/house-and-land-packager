"""StageLot data access."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from hlp.models.enums import LotStatus
from hlp.models.stage_lot import StageLot
from hlp.shared.exceptions import LotNotFoundError


def list_by_stage_paginated(
    db: Session,
    stage_id: int,
    page: int,
    size: int,
    status: LotStatus | None = None,
) -> tuple[list[StageLot], int]:
    base = select(StageLot).where(StageLot.stage_id == stage_id)
    if status is not None:
        base = base.where(StageLot.status == status)
    total = db.execute(select(func.count()).select_from(base.subquery())).scalar_one()
    stmt = base.order_by(StageLot.lot_number).offset((page - 1) * size).limit(size)
    items = list(db.execute(stmt).scalars().all())
    return items, int(total)


def get(db: Session, lot_id: int) -> StageLot | None:
    return db.get(StageLot, lot_id)


def get_by_stage_and_number(db: Session, stage_id: int, lot_number: str) -> StageLot | None:
    stmt = select(StageLot).where(
        StageLot.stage_id == stage_id, StageLot.lot_number == lot_number
    )
    return db.execute(stmt).scalar_one_or_none()


def create(db: Session, stage_id: int, **fields) -> StageLot:
    lot = StageLot(stage_id=stage_id, **fields)
    db.add(lot)
    db.flush()
    return lot


def create_bulk(db: Session, stage_id: int, lots_fields: list[dict]) -> list[StageLot]:
    created: list[StageLot] = []
    for fields in lots_fields:
        lot = StageLot(stage_id=stage_id, **fields)
        db.add(lot)
        created.append(lot)
    db.flush()
    return created


def update(db: Session, lot_id: int, **fields) -> StageLot:
    lot = get(db, lot_id)
    if lot is None:
        raise LotNotFoundError(f"Lot {lot_id} not found")
    for k, v in fields.items():
        setattr(lot, k, v)
    db.flush()
    return lot


def delete(db: Session, lot_id: int) -> None:
    lot = get(db, lot_id)
    if lot is None:
        raise LotNotFoundError(f"Lot {lot_id} not found")
    db.delete(lot)
    db.flush()

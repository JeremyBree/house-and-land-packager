"""EstateStage data access."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from hlp.models.estate_stage import EstateStage
from hlp.models.stage_lot import StageLot
from hlp.shared.exceptions import StageNotFoundError


def list_by_estate(db: Session, estate_id: int) -> list[EstateStage]:
    stmt = (
        select(EstateStage)
        .where(EstateStage.estate_id == estate_id)
        .order_by(EstateStage.name)
    )
    return list(db.execute(stmt).scalars().all())


def get(db: Session, stage_id: int) -> EstateStage | None:
    return db.get(EstateStage, stage_id)


def get_with_stats(db: Session, stage_id: int) -> tuple[EstateStage, int, dict[str, int]] | None:
    stmt = (
        select(EstateStage)
        .where(EstateStage.stage_id == stage_id)
        .options(joinedload(EstateStage.estate))
    )
    stage = db.execute(stmt).unique().scalar_one_or_none()
    if stage is None:
        return None
    count_stmt = select(func.count()).select_from(StageLot).where(StageLot.stage_id == stage_id)
    lot_count_actual = int(db.execute(count_stmt).scalar_one())
    breakdown_stmt = (
        select(StageLot.status, func.count())
        .where(StageLot.stage_id == stage_id)
        .group_by(StageLot.status)
    )
    rows = db.execute(breakdown_stmt).all()
    status_breakdown: dict[str, int] = {s.value: int(c) for s, c in rows}
    return stage, lot_count_actual, status_breakdown


def create(db: Session, estate_id: int, **fields) -> EstateStage:
    stage = EstateStage(estate_id=estate_id, **fields)
    db.add(stage)
    db.flush()
    return stage


def update(db: Session, stage_id: int, **fields) -> EstateStage:
    stage = get(db, stage_id)
    if stage is None:
        raise StageNotFoundError(f"Stage {stage_id} not found")
    for k, v in fields.items():
        setattr(stage, k, v)
    db.flush()
    return stage


def delete(db: Session, stage_id: int) -> None:
    stage = get(db, stage_id)
    if stage is None:
        raise StageNotFoundError(f"Stage {stage_id} not found")
    db.delete(stage)
    db.flush()

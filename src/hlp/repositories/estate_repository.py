"""Estate data access."""

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, joinedload

from hlp.models.estate import Estate
from hlp.shared.exceptions import NotFoundError


def list_paginated(
    db: Session,
    page: int,
    size: int,
    search: str | None = None,
    developer_id: int | None = None,
    region_id: int | None = None,
    active: bool | None = None,
) -> tuple[list[Estate], int]:
    base = select(Estate)
    if search:
        pattern = f"%{search.lower()}%"
        base = base.where(
            or_(
                func.lower(Estate.estate_name).like(pattern),
                func.lower(Estate.suburb).like(pattern),
            )
        )
    if developer_id is not None:
        base = base.where(Estate.developer_id == developer_id)
    if region_id is not None:
        base = base.where(Estate.region_id == region_id)
    if active is not None:
        base = base.where(Estate.active == active)

    total = db.execute(select(func.count()).select_from(base.subquery())).scalar_one()

    stmt = (
        base.order_by(Estate.estate_name)
        .offset((page - 1) * size)
        .limit(size)
    )
    items = list(db.execute(stmt).scalars().all())
    return items, int(total)


def get_with_relations(db: Session, estate_id: int) -> Estate | None:
    stmt = (
        select(Estate)
        .where(Estate.estate_id == estate_id)
        .options(joinedload(Estate.developer), joinedload(Estate.region))
    )
    return db.execute(stmt).scalar_one_or_none()


def get(db: Session, estate_id: int) -> Estate | None:
    return db.get(Estate, estate_id)


def create(db: Session, **fields) -> Estate:
    estate = Estate(**fields)
    db.add(estate)
    db.flush()
    return estate


def update(db: Session, estate_id: int, **fields) -> Estate:
    estate = get(db, estate_id)
    if estate is None:
        raise NotFoundError(f"Estate {estate_id} not found")
    for k, v in fields.items():
        if v is not None:
            setattr(estate, k, v)
    db.flush()
    return estate


def soft_delete(db: Session, estate_id: int) -> None:
    estate = get(db, estate_id)
    if estate is None:
        raise NotFoundError(f"Estate {estate_id} not found")
    estate.active = False
    db.flush()

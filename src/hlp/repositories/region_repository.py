"""Region data access."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from hlp.models.region import Region
from hlp.shared.exceptions import NotFoundError


def list_all(db: Session) -> list[Region]:
    stmt = select(Region).order_by(Region.name)
    return list(db.execute(stmt).scalars().all())


def get(db: Session, region_id: int) -> Region | None:
    return db.get(Region, region_id)


def create(db: Session, **fields) -> Region:
    region = Region(**fields)
    db.add(region)
    db.flush()
    return region


def update(db: Session, region_id: int, **fields) -> Region:
    region = get(db, region_id)
    if region is None:
        raise NotFoundError(f"Region {region_id} not found")
    for k, v in fields.items():
        if v is not None:
            setattr(region, k, v)
    db.flush()
    return region


def delete(db: Session, region_id: int) -> None:
    region = get(db, region_id)
    if region is None:
        raise NotFoundError(f"Region {region_id} not found")
    db.delete(region)
    db.flush()

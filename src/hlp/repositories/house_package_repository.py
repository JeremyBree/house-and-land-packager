"""HousePackage data access."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from hlp.models.house_package import HousePackage
from hlp.shared.exceptions import PackageNotFoundError


def list_filtered(
    db: Session,
    filters: dict,
    page: int,
    size: int,
) -> tuple[list[HousePackage], int]:
    base = select(HousePackage)
    if filters.get("estate_id") is not None:
        base = base.where(HousePackage.estate_id == filters["estate_id"])
    if filters.get("stage_id") is not None:
        base = base.where(HousePackage.stage_id == filters["stage_id"])
    if filters.get("brand"):
        base = base.where(HousePackage.brand == filters["brand"])
    if filters.get("design"):
        pattern = f"%{filters['design'].lower()}%"
        base = base.where(func.lower(HousePackage.design).like(pattern))
    if filters.get("facade"):
        pattern = f"%{filters['facade'].lower()}%"
        base = base.where(func.lower(HousePackage.facade).like(pattern))
    if filters.get("lot_number"):
        base = base.where(HousePackage.lot_number == filters["lot_number"])

    total = db.execute(select(func.count()).select_from(base.subquery())).scalar_one()
    stmt = (
        base.order_by(HousePackage.package_id.desc())
        .offset((page - 1) * size)
        .limit(size)
    )
    items = list(db.execute(stmt).scalars().all())
    return items, int(total)


def list_by_lot(
    db: Session, estate_id: int, stage_id: int, lot_number: str
) -> list[HousePackage]:
    stmt = select(HousePackage).where(
        HousePackage.estate_id == estate_id,
        HousePackage.stage_id == stage_id,
        HousePackage.lot_number == lot_number,
    )
    return list(db.execute(stmt).scalars().all())


def list_by_estate(db: Session, estate_id: int) -> list[HousePackage]:
    stmt = (
        select(HousePackage)
        .where(HousePackage.estate_id == estate_id)
        .order_by(HousePackage.stage_id, HousePackage.lot_number)
    )
    return list(db.execute(stmt).scalars().all())


def list_by_stage(db: Session, stage_id: int) -> list[HousePackage]:
    stmt = (
        select(HousePackage)
        .where(HousePackage.stage_id == stage_id)
        .order_by(HousePackage.lot_number)
    )
    return list(db.execute(stmt).scalars().all())


def list_all(db: Session) -> list[HousePackage]:
    stmt = select(HousePackage).order_by(HousePackage.estate_id, HousePackage.stage_id)
    return list(db.execute(stmt).scalars().all())


def get(db: Session, package_id: int) -> HousePackage | None:
    return db.get(HousePackage, package_id)


def create(db: Session, **fields) -> HousePackage:
    pkg = HousePackage(**fields)
    db.add(pkg)
    db.flush()
    return pkg


def update(db: Session, package_id: int, **fields) -> HousePackage:
    pkg = get(db, package_id)
    if pkg is None:
        raise PackageNotFoundError(f"Package {package_id} not found")
    for k, v in fields.items():
        if v is not None:
            setattr(pkg, k, v)
    db.flush()
    return pkg


def delete(db: Session, package_id: int) -> None:
    pkg = get(db, package_id)
    if pkg is None:
        raise PackageNotFoundError(f"Package {package_id} not found")
    db.delete(pkg)
    db.flush()

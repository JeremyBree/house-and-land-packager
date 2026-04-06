"""House design + facade data access."""

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from hlp.models.house_design import HouseDesign, HouseFacade


def list_by_brand(db: Session, brand: str) -> list[HouseDesign]:
    stmt = (
        select(HouseDesign)
        .where(HouseDesign.brand == brand, HouseDesign.active.is_(True))
        .options(joinedload(HouseDesign.facades))
        .order_by(HouseDesign.house_name)
    )
    return list(db.execute(stmt).unique().scalars().all())


def get(db: Session, design_id: int) -> HouseDesign | None:
    stmt = (
        select(HouseDesign)
        .where(HouseDesign.design_id == design_id)
        .options(joinedload(HouseDesign.facades), joinedload(HouseDesign.energy_ratings))
    )
    return db.execute(stmt).unique().scalars().first()


def get_by_name(db: Session, brand: str, house_name: str) -> HouseDesign | None:
    stmt = select(HouseDesign).where(
        HouseDesign.brand == brand,
        HouseDesign.house_name == house_name,
        HouseDesign.active.is_(True),
    )
    return db.execute(stmt).scalars().first()


def list_facades(db: Session, design_id: int) -> list[HouseFacade]:
    stmt = (
        select(HouseFacade)
        .where(HouseFacade.design_id == design_id)
        .order_by(HouseFacade.facade_name)
    )
    return list(db.execute(stmt).scalars().all())


def get_facade(db: Session, design_id: int, facade_name: str) -> HouseFacade | None:
    stmt = select(HouseFacade).where(
        HouseFacade.design_id == design_id,
        HouseFacade.facade_name == facade_name,
    )
    return db.execute(stmt).scalars().first()

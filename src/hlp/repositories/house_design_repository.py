"""House design + facade data access."""

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from hlp.models.energy_rating import EnergyRating
from hlp.models.house_design import HouseDesign, HouseFacade
from hlp.shared.exceptions import NotFoundError


def list_by_brand(db: Session, brand: str) -> list[HouseDesign]:
    stmt = (
        select(HouseDesign)
        .where(HouseDesign.brand == brand, HouseDesign.active.is_(True))
        .options(joinedload(HouseDesign.facades))
        .order_by(HouseDesign.house_name)
    )
    return list(db.execute(stmt).unique().scalars().all())


def list_all_by_brand(db: Session, brand: str) -> list[HouseDesign]:
    """List all designs for a brand, including inactive ones."""
    stmt = (
        select(HouseDesign)
        .where(HouseDesign.brand == brand)
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


def create_design(db: Session, **fields) -> HouseDesign:
    design = HouseDesign(**fields)
    db.add(design)
    db.flush()
    return design


def update_design(db: Session, design_id: int, **fields) -> HouseDesign:
    design = db.get(HouseDesign, design_id)
    if design is None:
        raise NotFoundError(f"House design {design_id} not found")
    for k, v in fields.items():
        setattr(design, k, v)
    db.flush()
    return design


def delete_design(db: Session, design_id: int) -> None:
    design = db.get(HouseDesign, design_id)
    if design is None:
        raise NotFoundError(f"House design {design_id} not found")
    db.delete(design)
    db.flush()


# ---- Facades ----

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


def create_facade(db: Session, design_id: int, **fields) -> HouseFacade:
    facade = HouseFacade(design_id=design_id, **fields)
    db.add(facade)
    db.flush()
    return facade


def update_facade(db: Session, facade_id: int, **fields) -> HouseFacade:
    facade = db.get(HouseFacade, facade_id)
    if facade is None:
        raise NotFoundError(f"Facade {facade_id} not found")
    for k, v in fields.items():
        setattr(facade, k, v)
    db.flush()
    return facade


def delete_facade(db: Session, facade_id: int) -> None:
    facade = db.get(HouseFacade, facade_id)
    if facade is None:
        raise NotFoundError(f"Facade {facade_id} not found")
    db.delete(facade)
    db.flush()


# ---- Energy Ratings ----

def list_energy_ratings(db: Session, design_id: int) -> list[EnergyRating]:
    stmt = (
        select(EnergyRating)
        .where(EnergyRating.design_id == design_id)
        .order_by(EnergyRating.garage_side, EnergyRating.orientation)
    )
    return list(db.execute(stmt).scalars().all())


def create_energy_rating(db: Session, design_id: int, **fields) -> EnergyRating:
    rating = EnergyRating(design_id=design_id, **fields)
    db.add(rating)
    db.flush()
    return rating


def update_energy_rating(db: Session, rating_id: int, **fields) -> EnergyRating:
    rating = db.get(EnergyRating, rating_id)
    if rating is None:
        raise NotFoundError(f"Energy rating {rating_id} not found")
    for k, v in fields.items():
        setattr(rating, k, v)
    db.flush()
    return rating


def delete_energy_rating(db: Session, rating_id: int) -> None:
    rating = db.get(EnergyRating, rating_id)
    if rating is None:
        raise NotFoundError(f"Energy rating {rating_id} not found")
    db.delete(rating)
    db.flush()

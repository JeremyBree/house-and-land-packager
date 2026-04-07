"""Upgrade category & item data access."""

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from hlp.models.upgrade import UpgradeCategory, UpgradeItem
from hlp.shared.exceptions import NotFoundError

# ---- Categories --------------------------------------------------------------

def list_categories(db: Session, brand: str | None = None) -> list[UpgradeCategory]:
    stmt = select(UpgradeCategory).order_by(UpgradeCategory.sort_order, UpgradeCategory.name)
    if brand:
        stmt = stmt.where(UpgradeCategory.brand == brand)
    return list(db.execute(stmt).scalars().all())


def get_category(db: Session, category_id: int) -> UpgradeCategory | None:
    return db.get(UpgradeCategory, category_id)


def create_category(db: Session, **fields) -> UpgradeCategory:
    cat = UpgradeCategory(**fields)
    db.add(cat)
    db.flush()
    return cat


def update_category(db: Session, category_id: int, **fields) -> UpgradeCategory:
    cat = get_category(db, category_id)
    if cat is None:
        raise NotFoundError(f"UpgradeCategory {category_id} not found")
    for k, v in fields.items():
        if v is not None:
            setattr(cat, k, v)
    db.flush()
    return cat


def delete_category(db: Session, category_id: int) -> None:
    cat = get_category(db, category_id)
    if cat is None:
        raise NotFoundError(f"UpgradeCategory {category_id} not found")
    db.delete(cat)
    db.flush()


# ---- Items -------------------------------------------------------------------

def list_items(
    db: Session,
    brand: str | None = None,
    category_id: int | None = None,
) -> list[UpgradeItem]:
    stmt = (
        select(UpgradeItem)
        .options(joinedload(UpgradeItem.category))
        .order_by(UpgradeItem.sort_order, UpgradeItem.description)
    )
    if brand:
        stmt = stmt.where(UpgradeItem.brand == brand)
    if category_id is not None:
        stmt = stmt.where(UpgradeItem.category_id == category_id)
    return list(db.execute(stmt).unique().scalars().all())


def list_by_brand(db: Session, brand: str) -> list[UpgradeItem]:
    """Legacy helper used by pricing engine."""
    return list_items(db, brand=brand)


def get_item(db: Session, upgrade_id: int) -> UpgradeItem | None:
    return db.get(UpgradeItem, upgrade_id)


def create_item(db: Session, **fields) -> UpgradeItem:
    item = UpgradeItem(**fields)
    db.add(item)
    db.flush()
    return item


def update_item(db: Session, upgrade_id: int, **fields) -> UpgradeItem:
    item = get_item(db, upgrade_id)
    if item is None:
        raise NotFoundError(f"UpgradeItem {upgrade_id} not found")
    for k, v in fields.items():
        if v is not None:
            setattr(item, k, v)
    db.flush()
    return item


def delete_item(db: Session, upgrade_id: int) -> None:
    item = get_item(db, upgrade_id)
    if item is None:
        raise NotFoundError(f"UpgradeItem {upgrade_id} not found")
    db.delete(item)
    db.flush()

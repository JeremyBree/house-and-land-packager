"""Upgrade catalog data access."""

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from hlp.models.upgrade import UpgradeCategory, UpgradeItem


def list_by_brand(db: Session, brand: str) -> list[UpgradeItem]:
    stmt = (
        select(UpgradeItem)
        .where(UpgradeItem.brand == brand)
        .options(joinedload(UpgradeItem.category))
        .order_by(UpgradeItem.sort_order)
    )
    return list(db.execute(stmt).unique().scalars().all())


def list_categories(db: Session, brand: str) -> list[UpgradeCategory]:
    stmt = (
        select(UpgradeCategory)
        .where(UpgradeCategory.brand == brand)
        .order_by(UpgradeCategory.sort_order)
    )
    return list(db.execute(stmt).scalars().all())

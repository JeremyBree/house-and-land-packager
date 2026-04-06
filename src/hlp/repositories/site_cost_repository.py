"""Site cost tier + item data access."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from hlp.models.postcode_site_cost import PostcodeSiteCost
from hlp.models.site_cost import SiteCostItem, SiteCostTier


def get_tier_for_fall(db: Session, fall_mm: int) -> SiteCostTier | None:
    stmt = select(SiteCostTier).where(
        SiteCostTier.fall_min_mm <= fall_mm,
        SiteCostTier.fall_max_mm >= fall_mm,
    )
    return db.execute(stmt).scalars().first()


def list_items_by_tier(db: Session, tier_id: int) -> list[SiteCostItem]:
    stmt = (
        select(SiteCostItem)
        .where(SiteCostItem.tier_id == tier_id)
        .order_by(SiteCostItem.sort_order)
    )
    return list(db.execute(stmt).scalars().all())


def list_base_items(db: Session) -> list[SiteCostItem]:
    stmt = (
        select(SiteCostItem)
        .where(SiteCostItem.tier_id.is_(None))
        .order_by(SiteCostItem.sort_order)
    )
    return list(db.execute(stmt).scalars().all())


def get_postcode_cost(db: Session, postcode: str) -> PostcodeSiteCost | None:
    return db.get(PostcodeSiteCost, postcode)

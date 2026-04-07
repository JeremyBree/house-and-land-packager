"""Pricing reference data access — travel surcharges, site costs, postcode costs, FBC bands."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from hlp.models.fbc_escalation import FbcEscalationBand
from hlp.models.postcode_site_cost import PostcodeSiteCost
from hlp.models.site_cost import SiteCostItem, SiteCostTier
from hlp.models.travel_surcharge import TravelSurcharge
from hlp.shared.exceptions import NotFoundError

# ── Travel Surcharges ──────────────────────────────────────────────


def list_travel_surcharges(db: Session) -> list[TravelSurcharge]:
    return list(
        db.execute(
            select(TravelSurcharge).order_by(TravelSurcharge.suburb_name)
        ).scalars().all()
    )


def get_travel_surcharge(db: Session, surcharge_id: int) -> TravelSurcharge:
    obj = db.get(TravelSurcharge, surcharge_id)
    if obj is None:
        raise NotFoundError(f"Travel surcharge {surcharge_id} not found")
    return obj


def create_travel_surcharge(db: Session, **fields) -> TravelSurcharge:
    obj = TravelSurcharge(**fields)
    db.add(obj)
    db.flush()
    return obj


def update_travel_surcharge(db: Session, surcharge_id: int, **fields) -> TravelSurcharge:
    obj = get_travel_surcharge(db, surcharge_id)
    for key, value in fields.items():
        setattr(obj, key, value)
    db.flush()
    return obj


def delete_travel_surcharge(db: Session, surcharge_id: int) -> None:
    obj = get_travel_surcharge(db, surcharge_id)
    db.delete(obj)
    db.flush()


# ── Site Cost Tiers ────────────────────────────────────────────────


def list_site_cost_tiers(db: Session) -> list[SiteCostTier]:
    return list(
        db.execute(
            select(SiteCostTier).order_by(SiteCostTier.fall_min_mm)
        ).scalars().all()
    )


def get_site_cost_tier(db: Session, tier_id: int) -> SiteCostTier:
    obj = db.get(SiteCostTier, tier_id)
    if obj is None:
        raise NotFoundError(f"Site cost tier {tier_id} not found")
    return obj


def create_site_cost_tier(db: Session, **fields) -> SiteCostTier:
    obj = SiteCostTier(**fields)
    db.add(obj)
    db.flush()
    return obj


def update_site_cost_tier(db: Session, tier_id: int, **fields) -> SiteCostTier:
    obj = get_site_cost_tier(db, tier_id)
    for key, value in fields.items():
        setattr(obj, key, value)
    db.flush()
    return obj


def delete_site_cost_tier(db: Session, tier_id: int) -> None:
    obj = get_site_cost_tier(db, tier_id)
    db.delete(obj)
    db.flush()


# ── Site Cost Items ────────────────────────────────────────────────


def list_site_cost_items(db: Session, tier_id: int | None = None) -> list[SiteCostItem]:
    stmt = select(SiteCostItem).order_by(SiteCostItem.sort_order, SiteCostItem.item_id)
    if tier_id is not None:
        stmt = stmt.where(SiteCostItem.tier_id == tier_id)
    return list(db.execute(stmt).scalars().all())


def get_site_cost_item(db: Session, item_id: int) -> SiteCostItem:
    obj = db.get(SiteCostItem, item_id)
    if obj is None:
        raise NotFoundError(f"Site cost item {item_id} not found")
    return obj


def create_site_cost_item(db: Session, **fields) -> SiteCostItem:
    obj = SiteCostItem(**fields)
    db.add(obj)
    db.flush()
    return obj


def update_site_cost_item(db: Session, item_id: int, **fields) -> SiteCostItem:
    obj = get_site_cost_item(db, item_id)
    for key, value in fields.items():
        setattr(obj, key, value)
    db.flush()
    return obj


def delete_site_cost_item(db: Session, item_id: int) -> None:
    obj = get_site_cost_item(db, item_id)
    db.delete(obj)
    db.flush()


# ── Postcode Site Costs ────────────────────────────────────────────


def list_postcode_site_costs(db: Session) -> list[PostcodeSiteCost]:
    return list(
        db.execute(
            select(PostcodeSiteCost).order_by(PostcodeSiteCost.postcode)
        ).scalars().all()
    )


def get_postcode_site_cost(db: Session, postcode: str) -> PostcodeSiteCost:
    obj = db.get(PostcodeSiteCost, postcode)
    if obj is None:
        raise NotFoundError(f"Postcode site cost '{postcode}' not found")
    return obj


def create_postcode_site_cost(db: Session, **fields) -> PostcodeSiteCost:
    obj = PostcodeSiteCost(**fields)
    db.add(obj)
    db.flush()
    return obj


def update_postcode_site_cost(db: Session, postcode: str, **fields) -> PostcodeSiteCost:
    obj = get_postcode_site_cost(db, postcode)
    for key, value in fields.items():
        setattr(obj, key, value)
    db.flush()
    return obj


def delete_postcode_site_cost(db: Session, postcode: str) -> None:
    obj = get_postcode_site_cost(db, postcode)
    db.delete(obj)
    db.flush()


# ── FBC Escalation Bands ──────────────────────────────────────────


def list_fbc_bands(db: Session, brand: str | None = None) -> list[FbcEscalationBand]:
    stmt = select(FbcEscalationBand).order_by(FbcEscalationBand.brand, FbcEscalationBand.day_start)
    if brand is not None:
        stmt = stmt.where(FbcEscalationBand.brand == brand)
    return list(db.execute(stmt).scalars().all())


def get_fbc_band(db: Session, band_id: int) -> FbcEscalationBand:
    obj = db.get(FbcEscalationBand, band_id)
    if obj is None:
        raise NotFoundError(f"FBC escalation band {band_id} not found")
    return obj


def create_fbc_band(db: Session, **fields) -> FbcEscalationBand:
    obj = FbcEscalationBand(**fields)
    db.add(obj)
    db.flush()
    return obj


def update_fbc_band(db: Session, band_id: int, **fields) -> FbcEscalationBand:
    obj = get_fbc_band(db, band_id)
    for key, value in fields.items():
        setattr(obj, key, value)
    db.flush()
    return obj


def delete_fbc_band(db: Session, band_id: int) -> None:
    obj = get_fbc_band(db, band_id)
    db.delete(obj)
    db.flush()

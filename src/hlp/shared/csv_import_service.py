"""Shared CSV import service — parse + bulk-create for 14 entity types."""

from __future__ import annotations

import csv
import io
from datetime import date
from decimal import Decimal, InvalidOperation

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from hlp.models.commission_rate import CommissionRate
from hlp.models.energy_rating import EnergyRating
from hlp.models.estate import Estate
from hlp.models.estate_stage import EstateStage
from hlp.models.fbc_escalation import FbcEscalationBand
from hlp.models.guideline import EstateDesignGuideline, GuidelineType
from hlp.models.house_design import HouseDesign, HouseFacade
from hlp.models.postcode_site_cost import PostcodeSiteCost
from hlp.models.profile import Profile
from hlp.models.site_cost import SiteCostItem, SiteCostTier
from hlp.models.travel_surcharge import TravelSurcharge
from hlp.models.upgrade import UpgradeCategory, UpgradeItem
from hlp.models.wholesale_group import WholesaleGroup

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _normalize_fields(reader: csv.DictReader) -> dict[str, str]:
    """Map lowercase-stripped field names back to original DictReader keys."""
    return {(name or "").strip().lower(): name for name in (reader.fieldnames or [])}


def _clean(val: str | None) -> str | None:
    if val is None:
        return None
    s = str(val).strip()
    return s if s else None


def _dec(val: str | None) -> Decimal | None:
    if not val or not str(val).strip():
        return None
    try:
        return Decimal(str(val).strip().replace(",", "").replace("$", ""))
    except (InvalidOperation, ValueError):
        return None


def _int_val(val: str | None) -> int | None:
    if not val or not str(val).strip():
        return None
    try:
        return int(float(str(val).strip()))
    except (ValueError, TypeError):
        return None


def _bool_val(val: str | None) -> bool:
    if not val:
        return False
    return str(val).strip().lower() in ("true", "yes", "y", "1")


def _date_val(val: str | None) -> date | None:
    if not val or not str(val).strip():
        return None
    s = str(val).strip()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"):
        try:
            if fmt == "%Y-%m-%d":
                return date.fromisoformat(s)
            return __import__("datetime").datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    return None


def _make_reader(content: bytes) -> csv.DictReader:
    text = content.decode("utf-8-sig")
    return csv.DictReader(io.StringIO(text))


def _get(row: dict, field_map: dict[str, str], key: str) -> str | None:
    """Get a value from a CSV row using normalised field lookup."""
    original = field_map.get(key)
    if original is None:
        return None
    return row.get(original)


# ---------------------------------------------------------------------------
# 1. House Designs
# ---------------------------------------------------------------------------

def parse_house_designs_csv(content: bytes) -> list[dict]:
    reader = _make_reader(content)
    fm = _normalize_fields(reader)
    rows = []
    for i, row in enumerate(reader, start=2):
        rows.append({
            "_row": i,
            "brand": _clean(_get(row, fm, "brand")),
            "house_name": _clean(_get(row, fm, "house_name")),
            "base_price": _dec(_get(row, fm, "base_price")),
            "storey": _clean(_get(row, fm, "storey")),
            "frontage": _dec(_get(row, fm, "frontage")),
            "depth": _dec(_get(row, fm, "depth")),
            "gf_sqm": _dec(_get(row, fm, "gf_sqm")),
            "total_sqm": _dec(_get(row, fm, "total_sqm")),
            "lot_total_sqm": _dec(_get(row, fm, "lot_total_sqm")),
            "squares": _int_val(_get(row, fm, "squares")),
            "details": _clean(_get(row, fm, "details")),
        })
    return rows


def bulk_create_house_designs(db: Session, rows: list[dict]) -> tuple[int, int, list[dict]]:
    created = 0
    skipped = 0
    errors: list[dict] = []
    for row in rows:
        r = row["_row"]
        brand = row.get("brand")
        house_name = row.get("house_name")
        if not brand or not house_name:
            errors.append({"row": r, "error": "brand and house_name are required"})
            continue
        existing = db.execute(
            select(HouseDesign).where(
                func.lower(HouseDesign.brand) == brand.lower(),
                func.lower(HouseDesign.house_name) == house_name.lower(),
            )
        ).scalar_one_or_none()
        if existing:
            skipped += 1
            continue
        try:
            obj = HouseDesign(
                brand=brand,
                house_name=house_name,
                base_price=row["base_price"] or 0,
                storey=row.get("storey") or "Single",
                frontage=row["frontage"] or 0,
                depth=row["depth"] or 0,
                gf_sqm=row["gf_sqm"] or 0,
                total_sqm=row["total_sqm"] or 0,
                lot_total_sqm=row["lot_total_sqm"] or 0,
                squares=row["squares"] or 0,
                details=row.get("details"),
                active=True,
            )
            db.add(obj)
            created += 1
        except Exception as exc:
            errors.append({"row": r, "error": str(exc)})
    return created, skipped, errors


# ---------------------------------------------------------------------------
# 2. House Facades
# ---------------------------------------------------------------------------

def parse_house_facades_csv(content: bytes) -> list[dict]:
    reader = _make_reader(content)
    fm = _normalize_fields(reader)
    rows = []
    for i, row in enumerate(reader, start=2):
        rows.append({
            "_row": i,
            "brand": _clean(_get(row, fm, "brand")),
            "house_name": _clean(_get(row, fm, "house_name")),
            "facade_name": _clean(_get(row, fm, "facade_name")),
            "facade_price": _dec(_get(row, fm, "facade_price")),
            "facade_details": _clean(_get(row, fm, "facade_details")),
            "is_included": _bool_val(_get(row, fm, "is_included")),
        })
    return rows


def bulk_create_house_facades(db: Session, rows: list[dict]) -> tuple[int, int, list[dict]]:
    created = 0
    skipped = 0
    errors: list[dict] = []
    design_cache: dict[tuple[str, str], int | None] = {}
    for row in rows:
        r = row["_row"]
        brand = row.get("brand")
        house_name = row.get("house_name")
        facade_name = row.get("facade_name")
        if not brand or not house_name or not facade_name:
            errors.append({"row": r, "error": "brand, house_name, and facade_name are required"})
            continue
        cache_key = (brand.lower(), house_name.lower())
        if cache_key not in design_cache:
            design = db.execute(
                select(HouseDesign).where(
                    func.lower(HouseDesign.brand) == brand.lower(),
                    func.lower(HouseDesign.house_name) == house_name.lower(),
                )
            ).scalar_one_or_none()
            design_cache[cache_key] = design.design_id if design else None
        design_id = design_cache[cache_key]
        if design_id is None:
            errors.append({"row": r, "error": f"HouseDesign not found: {brand} / {house_name}"})
            continue
        existing = db.execute(
            select(HouseFacade).where(
                HouseFacade.design_id == design_id,
                func.lower(HouseFacade.facade_name) == facade_name.lower(),
            )
        ).scalar_one_or_none()
        if existing:
            skipped += 1
            continue
        try:
            obj = HouseFacade(
                design_id=design_id,
                facade_name=facade_name,
                facade_price=row["facade_price"] or 0,
                facade_details=row.get("facade_details"),
                is_included=row.get("is_included", False),
            )
            db.add(obj)
            created += 1
        except Exception as exc:
            errors.append({"row": r, "error": str(exc)})
    return created, skipped, errors


# ---------------------------------------------------------------------------
# 3. Energy Ratings
# ---------------------------------------------------------------------------

def parse_energy_ratings_csv(content: bytes) -> list[dict]:
    reader = _make_reader(content)
    fm = _normalize_fields(reader)
    rows = []
    for i, row in enumerate(reader, start=2):
        rows.append({
            "_row": i,
            "brand": _clean(_get(row, fm, "brand")),
            "house_name": _clean(_get(row, fm, "house_name")),
            "garage_side": _clean(_get(row, fm, "garage_side")),
            "orientation": _clean(_get(row, fm, "orientation")),
            "star_rating": _dec(_get(row, fm, "star_rating")),
            "best_worst": _clean(_get(row, fm, "best_worst")),
            "compliance_cost": _dec(_get(row, fm, "compliance_cost")),
        })
    return rows


def bulk_create_energy_ratings(db: Session, rows: list[dict]) -> tuple[int, int, list[dict]]:
    created = 0
    skipped = 0
    errors: list[dict] = []
    design_cache: dict[tuple[str, str], int | None] = {}
    for row in rows:
        r = row["_row"]
        brand = row.get("brand")
        house_name = row.get("house_name")
        garage_side = row.get("garage_side")
        orientation = row.get("orientation")
        if not brand or not house_name or not garage_side or not orientation:
            errors.append({"row": r, "error": "brand, house_name, garage_side, and orientation are required"})
            continue
        cache_key = (brand.lower(), house_name.lower())
        if cache_key not in design_cache:
            design = db.execute(
                select(HouseDesign).where(
                    func.lower(HouseDesign.brand) == brand.lower(),
                    func.lower(HouseDesign.house_name) == house_name.lower(),
                )
            ).scalar_one_or_none()
            design_cache[cache_key] = design.design_id if design else None
        design_id = design_cache[cache_key]
        if design_id is None:
            errors.append({"row": r, "error": f"HouseDesign not found: {brand} / {house_name}"})
            continue
        existing = db.execute(
            select(EnergyRating).where(
                EnergyRating.design_id == design_id,
                func.lower(EnergyRating.garage_side) == garage_side.lower(),
                func.lower(EnergyRating.orientation) == orientation.lower(),
            )
        ).scalar_one_or_none()
        if existing:
            skipped += 1
            continue
        try:
            obj = EnergyRating(
                design_id=design_id,
                garage_side=garage_side,
                orientation=orientation,
                star_rating=row["star_rating"] or 0,
                best_worst=row.get("best_worst") or "B",
                compliance_cost=row["compliance_cost"] or 0,
            )
            db.add(obj)
            created += 1
        except Exception as exc:
            errors.append({"row": r, "error": str(exc)})
    return created, skipped, errors


# ---------------------------------------------------------------------------
# 4. FBC Escalation Bands
# ---------------------------------------------------------------------------

def parse_fbc_bands_csv(content: bytes) -> list[dict]:
    reader = _make_reader(content)
    fm = _normalize_fields(reader)
    rows = []
    for i, row in enumerate(reader, start=2):
        rows.append({
            "_row": i,
            "brand": _clean(_get(row, fm, "brand")),
            "day_start": _int_val(_get(row, fm, "day_start")),
            "day_end": _int_val(_get(row, fm, "day_end")),
            "multiplier": _dec(_get(row, fm, "multiplier")),
        })
    return rows


def bulk_create_fbc_bands(db: Session, rows: list[dict]) -> tuple[int, int, list[dict]]:
    created = 0
    skipped = 0
    errors: list[dict] = []
    for row in rows:
        r = row["_row"]
        brand = row.get("brand")
        day_start = row.get("day_start")
        if not brand or day_start is None:
            errors.append({"row": r, "error": "brand and day_start are required"})
            continue
        existing = db.execute(
            select(FbcEscalationBand).where(
                func.lower(FbcEscalationBand.brand) == brand.lower(),
                FbcEscalationBand.day_start == day_start,
            )
        ).scalar_one_or_none()
        if existing:
            skipped += 1
            continue
        try:
            obj = FbcEscalationBand(
                brand=brand,
                day_start=day_start,
                day_end=row.get("day_end") or 0,
                multiplier=row.get("multiplier") or 0,
            )
            db.add(obj)
            created += 1
        except Exception as exc:
            errors.append({"row": r, "error": str(exc)})
    return created, skipped, errors


# ---------------------------------------------------------------------------
# 5. Upgrade Categories
# ---------------------------------------------------------------------------

def parse_upgrade_categories_csv(content: bytes) -> list[dict]:
    reader = _make_reader(content)
    fm = _normalize_fields(reader)
    rows = []
    for i, row in enumerate(reader, start=2):
        rows.append({
            "_row": i,
            "brand": _clean(_get(row, fm, "brand")),
            "name": _clean(_get(row, fm, "name")),
            "sort_order": _int_val(_get(row, fm, "sort_order")),
        })
    return rows


def bulk_create_upgrade_categories(db: Session, rows: list[dict]) -> tuple[int, int, list[dict]]:
    created = 0
    skipped = 0
    errors: list[dict] = []
    for row in rows:
        r = row["_row"]
        brand = row.get("brand")
        name = row.get("name")
        if not brand or not name:
            errors.append({"row": r, "error": "brand and name are required"})
            continue
        existing = db.execute(
            select(UpgradeCategory).where(
                func.lower(UpgradeCategory.brand) == brand.lower(),
                func.lower(UpgradeCategory.name) == name.lower(),
            )
        ).scalar_one_or_none()
        if existing:
            skipped += 1
            continue
        try:
            obj = UpgradeCategory(
                brand=brand,
                name=name,
                sort_order=row.get("sort_order") or 0,
            )
            db.add(obj)
            created += 1
        except Exception as exc:
            errors.append({"row": r, "error": str(exc)})
    return created, skipped, errors


# ---------------------------------------------------------------------------
# 6. Upgrade Items
# ---------------------------------------------------------------------------

def parse_upgrade_items_csv(content: bytes) -> list[dict]:
    reader = _make_reader(content)
    fm = _normalize_fields(reader)
    rows = []
    for i, row in enumerate(reader, start=2):
        rows.append({
            "_row": i,
            "brand": _clean(_get(row, fm, "brand")),
            "category_name": _clean(_get(row, fm, "category_name")),
            "description": _clean(_get(row, fm, "description")),
            "price": _dec(_get(row, fm, "price")),
            "date_added": _date_val(_get(row, fm, "date_added")),
            "notes": _clean(_get(row, fm, "notes")),
            "sort_order": _int_val(_get(row, fm, "sort_order")),
        })
    return rows


def bulk_create_upgrade_items(db: Session, rows: list[dict]) -> tuple[int, int, list[dict]]:
    created = 0
    skipped = 0
    errors: list[dict] = []
    cat_cache: dict[tuple[str, str], int | None] = {}
    for row in rows:
        r = row["_row"]
        brand = row.get("brand")
        description = row.get("description")
        if not brand or not description:
            errors.append({"row": r, "error": "brand and description are required"})
            continue
        # resolve category
        category_name = row.get("category_name")
        category_id = None
        if category_name:
            cache_key = (brand.lower(), category_name.lower())
            if cache_key not in cat_cache:
                cat = db.execute(
                    select(UpgradeCategory).where(
                        func.lower(UpgradeCategory.brand) == brand.lower(),
                        func.lower(UpgradeCategory.name) == category_name.lower(),
                    )
                ).scalar_one_or_none()
                cat_cache[cache_key] = cat.category_id if cat else None
            category_id = cat_cache[cache_key]
            if category_id is None:
                errors.append({"row": r, "error": f"UpgradeCategory not found: {brand} / {category_name}"})
                continue
        # unique check by brand + description
        existing = db.execute(
            select(UpgradeItem).where(
                func.lower(UpgradeItem.brand) == brand.lower(),
                func.lower(UpgradeItem.description) == description.lower(),
            )
        ).scalar_one_or_none()
        if existing:
            skipped += 1
            continue
        try:
            obj = UpgradeItem(
                brand=brand,
                category_id=category_id,
                description=description,
                price=row["price"] or 0,
                date_added=row.get("date_added"),
                notes=row.get("notes"),
                sort_order=row.get("sort_order") or 0,
            )
            db.add(obj)
            created += 1
        except Exception as exc:
            errors.append({"row": r, "error": str(exc)})
    return created, skipped, errors


# ---------------------------------------------------------------------------
# 7. Wholesale Groups
# ---------------------------------------------------------------------------

def parse_wholesale_groups_csv(content: bytes) -> list[dict]:
    reader = _make_reader(content)
    fm = _normalize_fields(reader)
    rows = []
    for i, row in enumerate(reader, start=2):
        rows.append({
            "_row": i,
            "group_name": _clean(_get(row, fm, "group_name")),
            "gst_registered": _bool_val(_get(row, fm, "gst_registered")),
            "active": _bool_val(_get(row, fm, "active")),
        })
    return rows


def bulk_create_wholesale_groups(db: Session, rows: list[dict]) -> tuple[int, int, list[dict]]:
    created = 0
    skipped = 0
    errors: list[dict] = []
    for row in rows:
        r = row["_row"]
        group_name = row.get("group_name")
        if not group_name:
            errors.append({"row": r, "error": "group_name is required"})
            continue
        existing = db.execute(
            select(WholesaleGroup).where(
                func.lower(WholesaleGroup.group_name) == group_name.lower(),
            )
        ).scalar_one_or_none()
        if existing:
            skipped += 1
            continue
        try:
            obj = WholesaleGroup(
                group_name=group_name,
                gst_registered=row.get("gst_registered", False),
                active=row.get("active", True),
            )
            db.add(obj)
            created += 1
        except Exception as exc:
            errors.append({"row": r, "error": str(exc)})
    return created, skipped, errors


# ---------------------------------------------------------------------------
# 8. Commission Rates
# ---------------------------------------------------------------------------

def parse_commission_rates_csv(content: bytes) -> list[dict]:
    reader = _make_reader(content)
    fm = _normalize_fields(reader)
    rows = []
    for i, row in enumerate(reader, start=2):
        rows.append({
            "_row": i,
            "brand": _clean(_get(row, fm, "brand")),
            "bdm_name": _clean(_get(row, fm, "bdm_name")),
            "group_name": _clean(_get(row, fm, "group_name")),
            "commission_fixed": _dec(_get(row, fm, "commission_fixed")),
            "commission_pct": _dec(_get(row, fm, "commission_pct")),
        })
    return rows


def bulk_create_commission_rates(db: Session, rows: list[dict]) -> tuple[int, int, list[dict]]:
    created = 0
    skipped = 0
    errors: list[dict] = []
    bdm_cache: dict[str, int | None] = {}
    group_cache: dict[str, int | None] = {}
    for row in rows:
        r = row["_row"]
        brand = row.get("brand")
        bdm_name = row.get("bdm_name")
        group_name = row.get("group_name")
        if not brand or not bdm_name or not group_name:
            errors.append({"row": r, "error": "brand, bdm_name, and group_name are required"})
            continue
        # resolve BDM profile by first_name
        bdm_key = bdm_name.lower()
        if bdm_key not in bdm_cache:
            profile = db.execute(
                select(Profile).where(
                    func.lower(Profile.first_name) == bdm_key,
                )
            ).scalar_one_or_none()
            bdm_cache[bdm_key] = profile.profile_id if profile else None
        bdm_profile_id = bdm_cache[bdm_key]
        if bdm_profile_id is None:
            errors.append({"row": r, "error": f"BDM Profile not found for first_name: {bdm_name}"})
            continue
        # resolve wholesale group
        grp_key = group_name.lower()
        if grp_key not in group_cache:
            grp = db.execute(
                select(WholesaleGroup).where(
                    func.lower(WholesaleGroup.group_name) == grp_key,
                )
            ).scalar_one_or_none()
            group_cache[grp_key] = grp.group_id if grp else None
        group_id = group_cache[grp_key]
        if group_id is None:
            errors.append({"row": r, "error": f"WholesaleGroup not found: {group_name}"})
            continue
        existing = db.execute(
            select(CommissionRate).where(
                CommissionRate.bdm_profile_id == bdm_profile_id,
                CommissionRate.group_id == group_id,
            )
        ).scalar_one_or_none()
        if existing:
            skipped += 1
            continue
        try:
            cf = row.get("commission_fixed")
            cp = row.get("commission_pct")
            obj = CommissionRate(
                bdm_profile_id=bdm_profile_id,
                group_id=group_id,
                brand=brand,
                commission_fixed=float(cf) if cf is not None else None,
                commission_pct=float(cp) if cp is not None else None,
            )
            db.add(obj)
            created += 1
        except Exception as exc:
            errors.append({"row": r, "error": str(exc)})
    return created, skipped, errors


# ---------------------------------------------------------------------------
# 9. Travel Surcharges
# ---------------------------------------------------------------------------

def parse_travel_surcharges_csv(content: bytes) -> list[dict]:
    reader = _make_reader(content)
    fm = _normalize_fields(reader)
    rows = []
    for i, row in enumerate(reader, start=2):
        rows.append({
            "_row": i,
            "suburb_name": _clean(_get(row, fm, "suburb_name")),
            "postcode": _clean(_get(row, fm, "postcode")),
            "surcharge_amount": _dec(_get(row, fm, "surcharge_amount")),
            "region_name": _clean(_get(row, fm, "region_name")),
        })
    return rows


def bulk_create_travel_surcharges(db: Session, rows: list[dict]) -> tuple[int, int, list[dict]]:
    created = 0
    skipped = 0
    errors: list[dict] = []
    for row in rows:
        r = row["_row"]
        suburb_name = row.get("suburb_name")
        if not suburb_name:
            errors.append({"row": r, "error": "suburb_name is required"})
            continue
        existing = db.execute(
            select(TravelSurcharge).where(
                func.lower(TravelSurcharge.suburb_name) == suburb_name.lower(),
            )
        ).scalar_one_or_none()
        if existing:
            skipped += 1
            continue
        try:
            obj = TravelSurcharge(
                suburb_name=suburb_name,
                postcode=row.get("postcode"),
                surcharge_amount=float(row.get("surcharge_amount") or 0),
                region_name=row.get("region_name"),
            )
            db.add(obj)
            created += 1
        except Exception as exc:
            errors.append({"row": r, "error": str(exc)})
    return created, skipped, errors


# ---------------------------------------------------------------------------
# 10. Postcode Site Costs
# ---------------------------------------------------------------------------

def parse_postcode_costs_csv(content: bytes) -> list[dict]:
    reader = _make_reader(content)
    fm = _normalize_fields(reader)
    rows = []
    for i, row in enumerate(reader, start=2):
        rows.append({
            "_row": i,
            "postcode": _clean(_get(row, fm, "postcode")),
            "rock_removal_cost": _dec(_get(row, fm, "rock_removal_cost")),
        })
    return rows


def bulk_create_postcode_costs(db: Session, rows: list[dict]) -> tuple[int, int, list[dict]]:
    created = 0
    skipped = 0
    errors: list[dict] = []
    for row in rows:
        r = row["_row"]
        postcode = row.get("postcode")
        if not postcode:
            errors.append({"row": r, "error": "postcode is required"})
            continue
        existing = db.execute(
            select(PostcodeSiteCost).where(PostcodeSiteCost.postcode == postcode)
        ).scalar_one_or_none()
        if existing:
            skipped += 1
            continue
        try:
            obj = PostcodeSiteCost(
                postcode=postcode,
                rock_removal_cost=float(row.get("rock_removal_cost") or 0),
            )
            db.add(obj)
            created += 1
        except Exception as exc:
            errors.append({"row": r, "error": str(exc)})
    return created, skipped, errors


# ---------------------------------------------------------------------------
# 11. Site Cost Tiers
# ---------------------------------------------------------------------------

def parse_site_cost_tiers_csv(content: bytes) -> list[dict]:
    reader = _make_reader(content)
    fm = _normalize_fields(reader)
    rows = []
    for i, row in enumerate(reader, start=2):
        rows.append({
            "_row": i,
            "tier_name": _clean(_get(row, fm, "tier_name")),
            "fall_min_mm": _int_val(_get(row, fm, "fall_min_mm")),
            "fall_max_mm": _int_val(_get(row, fm, "fall_max_mm")),
        })
    return rows


def bulk_create_site_cost_tiers(db: Session, rows: list[dict]) -> tuple[int, int, list[dict]]:
    created = 0
    skipped = 0
    errors: list[dict] = []
    for row in rows:
        r = row["_row"]
        tier_name = row.get("tier_name")
        if not tier_name:
            errors.append({"row": r, "error": "tier_name is required"})
            continue
        existing = db.execute(
            select(SiteCostTier).where(
                func.lower(SiteCostTier.tier_name) == tier_name.lower(),
            )
        ).scalar_one_or_none()
        if existing:
            skipped += 1
            continue
        try:
            obj = SiteCostTier(
                tier_name=tier_name,
                fall_min_mm=row.get("fall_min_mm") or 0,
                fall_max_mm=row.get("fall_max_mm") or 0,
            )
            db.add(obj)
            created += 1
        except Exception as exc:
            errors.append({"row": r, "error": str(exc)})
    return created, skipped, errors


# ---------------------------------------------------------------------------
# 12. Site Cost Items
# ---------------------------------------------------------------------------

def parse_site_cost_items_csv(content: bytes) -> list[dict]:
    reader = _make_reader(content)
    fm = _normalize_fields(reader)
    rows = []
    for i, row in enumerate(reader, start=2):
        rows.append({
            "_row": i,
            "tier_name": _clean(_get(row, fm, "tier_name")),
            "item_name": _clean(_get(row, fm, "item_name")),
            "condition_type": _clean(_get(row, fm, "condition_type")),
            "condition_description": _clean(_get(row, fm, "condition_description")),
            "cost_single_lt190": _dec(_get(row, fm, "cost_single_lt190")),
            "cost_double_lt190": _dec(_get(row, fm, "cost_double_lt190")),
            "cost_single_191_249": _dec(_get(row, fm, "cost_single_191_249")),
            "cost_double_191_249": _dec(_get(row, fm, "cost_double_191_249")),
            "cost_single_250_300": _dec(_get(row, fm, "cost_single_250_300")),
            "cost_double_250_300": _dec(_get(row, fm, "cost_double_250_300")),
            "cost_single_300plus": _dec(_get(row, fm, "cost_single_300plus")),
            "cost_double_300plus": _dec(_get(row, fm, "cost_double_300plus")),
            "sort_order": _int_val(_get(row, fm, "sort_order")),
        })
    return rows


def bulk_create_site_cost_items(db: Session, rows: list[dict]) -> tuple[int, int, list[dict]]:
    created = 0
    skipped = 0
    errors: list[dict] = []
    tier_cache: dict[str, int | None] = {}
    for row in rows:
        r = row["_row"]
        item_name = row.get("item_name")
        if not item_name:
            errors.append({"row": r, "error": "item_name is required"})
            continue
        tier_name = row.get("tier_name")
        tier_id = None
        if tier_name:
            tk = tier_name.lower()
            if tk not in tier_cache:
                tier = db.execute(
                    select(SiteCostTier).where(
                        func.lower(SiteCostTier.tier_name) == tk,
                    )
                ).scalar_one_or_none()
                tier_cache[tk] = tier.tier_id if tier else None
            tier_id = tier_cache[tk]
            if tier_id is None:
                errors.append({"row": r, "error": f"SiteCostTier not found: {tier_name}"})
                continue
        # unique check
        stmt = select(SiteCostItem).where(
            func.lower(SiteCostItem.item_name) == item_name.lower(),
        )
        if tier_id is not None:
            stmt = stmt.where(SiteCostItem.tier_id == tier_id)
        else:
            stmt = stmt.where(SiteCostItem.tier_id.is_(None))
        existing = db.execute(stmt).scalar_one_or_none()
        if existing:
            skipped += 1
            continue
        try:
            obj = SiteCostItem(
                tier_id=tier_id,
                item_name=item_name,
                condition_type=row.get("condition_type"),
                condition_description=row.get("condition_description"),
                cost_single_lt190=row.get("cost_single_lt190"),
                cost_double_lt190=row.get("cost_double_lt190"),
                cost_single_191_249=row.get("cost_single_191_249"),
                cost_double_191_249=row.get("cost_double_191_249"),
                cost_single_250_300=row.get("cost_single_250_300"),
                cost_double_250_300=row.get("cost_double_250_300"),
                cost_single_300plus=row.get("cost_single_300plus"),
                cost_double_300plus=row.get("cost_double_300plus"),
                sort_order=row.get("sort_order") or 0,
            )
            db.add(obj)
            created += 1
        except Exception as exc:
            errors.append({"row": r, "error": str(exc)})
    return created, skipped, errors


# ---------------------------------------------------------------------------
# 13. Guideline Types
# ---------------------------------------------------------------------------

def parse_guideline_types_csv(content: bytes) -> list[dict]:
    reader = _make_reader(content)
    fm = _normalize_fields(reader)
    rows = []
    for i, row in enumerate(reader, start=2):
        rows.append({
            "_row": i,
            "short_name": _clean(_get(row, fm, "short_name")),
            "description": _clean(_get(row, fm, "description")),
            "sort_order": _int_val(_get(row, fm, "sort_order")),
            "category_code": _clean(_get(row, fm, "category_code")),
            "category_name": _clean(_get(row, fm, "category_name")),
            "notes": _clean(_get(row, fm, "notes")),
            "default_price": _dec(_get(row, fm, "default_price")),
        })
    return rows


def bulk_create_guideline_types(db: Session, rows: list[dict]) -> tuple[int, int, list[dict]]:
    created = 0
    skipped = 0
    errors: list[dict] = []
    for row in rows:
        r = row["_row"]
        short_name = row.get("short_name")
        if not short_name:
            errors.append({"row": r, "error": "short_name is required"})
            continue
        existing = db.execute(
            select(GuidelineType).where(
                func.lower(GuidelineType.short_name) == short_name.lower(),
            )
        ).scalar_one_or_none()
        if existing:
            skipped += 1
            continue
        try:
            obj = GuidelineType(
                short_name=short_name,
                description=row.get("description") or short_name,
                sort_order=row.get("sort_order") or 0,
                category_code=row.get("category_code") or short_name,
                category_name=row.get("category_name"),
                notes=row.get("notes"),
                default_price=row.get("default_price") or 0,
            )
            db.add(obj)
            created += 1
        except Exception as exc:
            errors.append({"row": r, "error": str(exc)})
    return created, skipped, errors


# ---------------------------------------------------------------------------
# 14. Estate Design Guidelines
# ---------------------------------------------------------------------------

def parse_estate_guidelines_csv(content: bytes) -> list[dict]:
    reader = _make_reader(content)
    fm = _normalize_fields(reader)
    rows = []
    for i, row in enumerate(reader, start=2):
        rows.append({
            "_row": i,
            "estate_name": _clean(_get(row, fm, "estate_name")),
            "stage_name": _clean(_get(row, fm, "stage_name")),
            "guideline_type": _clean(_get(row, fm, "guideline_type")),
            "cost": _dec(_get(row, fm, "cost")),
            "override_text": _clean(_get(row, fm, "override_text")),
        })
    return rows


def bulk_create_estate_guidelines(db: Session, rows: list[dict]) -> tuple[int, int, list[dict]]:
    created = 0
    skipped = 0
    errors: list[dict] = []
    estate_cache: dict[str, int | None] = {}
    stage_cache: dict[tuple[int, str], int | None] = {}
    type_cache: dict[str, int | None] = {}
    for row in rows:
        r = row["_row"]
        estate_name = row.get("estate_name")
        guideline_type = row.get("guideline_type")
        if not estate_name or not guideline_type:
            errors.append({"row": r, "error": "estate_name and guideline_type are required"})
            continue
        # resolve estate
        ek = estate_name.lower()
        if ek not in estate_cache:
            estate = db.execute(
                select(Estate).where(func.lower(Estate.estate_name) == ek)
            ).scalar_one_or_none()
            estate_cache[ek] = estate.estate_id if estate else None
        estate_id = estate_cache[ek]
        if estate_id is None:
            errors.append({"row": r, "error": f"Estate not found: {estate_name}"})
            continue
        # resolve stage (optional)
        stage_name = row.get("stage_name")
        stage_id = None
        if stage_name:
            sk = (estate_id, stage_name.lower())
            if sk not in stage_cache:
                stage = db.execute(
                    select(EstateStage).where(
                        EstateStage.estate_id == estate_id,
                        func.lower(EstateStage.name) == stage_name.lower(),
                    )
                ).scalar_one_or_none()
                stage_cache[sk] = stage.stage_id if stage else None
            stage_id = stage_cache[sk]
            if stage_id is None:
                errors.append({"row": r, "error": f"Stage not found: {stage_name} in estate {estate_name}"})
                continue
        # resolve guideline type
        tk = guideline_type.lower()
        if tk not in type_cache:
            gt = db.execute(
                select(GuidelineType).where(
                    func.lower(GuidelineType.short_name) == tk,
                )
            ).scalar_one_or_none()
            type_cache[tk] = gt.type_id if gt else None
        type_id = type_cache[tk]
        if type_id is None:
            errors.append({"row": r, "error": f"GuidelineType not found: {guideline_type}"})
            continue
        # unique check
        stmt = select(EstateDesignGuideline).where(
            EstateDesignGuideline.estate_id == estate_id,
            EstateDesignGuideline.type_id == type_id,
        )
        if stage_id is not None:
            stmt = stmt.where(EstateDesignGuideline.stage_id == stage_id)
        else:
            stmt = stmt.where(EstateDesignGuideline.stage_id.is_(None))
        existing = db.execute(stmt).scalar_one_or_none()
        if existing:
            skipped += 1
            continue
        try:
            obj = EstateDesignGuideline(
                estate_id=estate_id,
                stage_id=stage_id,
                type_id=type_id,
                cost=float(row["cost"]) if row.get("cost") is not None else None,
                override_text=row.get("override_text"),
            )
            db.add(obj)
            created += 1
        except Exception as exc:
            errors.append({"row": r, "error": str(exc)})
    return created, skipped, errors

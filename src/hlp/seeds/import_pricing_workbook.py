"""Import pricing data from the Hermitage Homes Excel workbook into the database.

Usage:
    python -m hlp.seeds.import_pricing_workbook <path_to_xlsm> [--brand "Hermitage Homes"]

All operations are idempotent (upsert on unique constraints).
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Any

import openpyxl
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

logger = logging.getLogger(__name__)


@dataclass
class ImportResult:
    houses_created: int = 0
    facades_created: int = 0
    energy_ratings_created: int = 0
    upgrades_created: int = 0
    upgrade_categories_created: int = 0
    wholesale_groups_created: int = 0
    commission_rates_created: int = 0
    travel_surcharges_created: int = 0
    postcode_costs_created: int = 0
    guideline_types_created: int = 0
    estate_guidelines_created: int = 0
    fbc_bands_created: int = 0
    site_cost_tiers_created: int = 0
    site_cost_items_created: int = 0
    skipped: int = 0
    errors: list = field(default_factory=list)

    def merge(self, other: ImportResult) -> None:
        """Add counts from another ImportResult into this one."""
        for f in [
            "houses_created", "facades_created", "energy_ratings_created",
            "upgrades_created", "upgrade_categories_created",
            "wholesale_groups_created", "commission_rates_created",
            "travel_surcharges_created", "postcode_costs_created",
            "guideline_types_created", "estate_guidelines_created",
            "fbc_bands_created", "site_cost_tiers_created",
            "site_cost_items_created", "skipped",
        ]:
            setattr(self, f, getattr(self, f) + getattr(other, f))
        self.errors.extend(other.errors)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _clean_str(val: Any) -> str | None:
    """Strip whitespace and normalise a cell value to a string or None."""
    if val is None:
        return None
    s = str(val).strip()
    # Normalise smart quotes
    s = s.replace("\u2018", "'").replace("\u2019", "'")
    s = s.replace("\u201c", '"').replace("\u201d", '"')
    if not s:
        return None
    return s


def _to_decimal(val: Any) -> Decimal | None:
    """Convert a cell value to Decimal safely."""
    if val is None:
        return None
    if isinstance(val, bool):
        return None
    if isinstance(val, str):
        val = val.strip().replace(",", "").replace("$", "")
        if not val:
            return None
    try:
        return Decimal(str(val))
    except (InvalidOperation, ValueError):
        return None


def _to_int(val: Any) -> int | None:
    """Convert a cell value to int."""
    if val is None:
        return None
    if isinstance(val, bool):
        return None
    try:
        return int(float(val))
    except (ValueError, TypeError):
        return None


def _to_date(val: Any) -> date | None:
    """Convert a cell value (possibly datetime) to a date."""
    if val is None:
        return None
    if isinstance(val, datetime):
        return val.date()
    if isinstance(val, date):
        return val
    return None


def _cell(ws, row: int, col: int) -> Any:
    """Read a cell value from a worksheet."""
    return ws.cell(row, col).value


# ---------------------------------------------------------------------------
# 1. House Designs + Facades
# ---------------------------------------------------------------------------

def _import_house_designs(db: Session, ws, brand: str) -> ImportResult:
    """Import house designs and facades from the Houses sheet (Table1 area).

    Layout (row 3 = headers, data starts row 4):
      A=House, B=Price, C=Storey, D=Frontage, E=Depth, F=GF m2, G=Total m2,
      H=Lot Total, I=Squares, J=House Details, K=Facade, L=Facade Price,
      M=Facade Details
    Each (house, facade) combo is a separate row.
    """
    result = ImportResult()

    # Cache of existing designs keyed by (brand, house_name)
    design_cache: dict[str, HouseDesign] = {}
    existing = db.query(HouseDesign).filter(HouseDesign.brand == brand).all()
    for d in existing:
        design_cache[d.house_name] = d

    # Cache existing facades keyed by (design_id, facade_name)
    facade_cache: set[tuple[int, str]] = set()
    existing_facades = db.query(HouseFacade).join(HouseDesign).filter(
        HouseDesign.brand == brand
    ).all()
    for f in existing_facades:
        facade_cache.add((f.design_id, f.facade_name))

    row = 4
    while True:
        house_name = _clean_str(_cell(ws, row, 1))
        if house_name is None:
            # Check a few more rows in case there's a gap
            if all(_clean_str(_cell(ws, row + i, 1)) is None for i in range(3)):
                break
            row += 1
            result.skipped += 1
            continue

        try:
            # Get or create the design
            if house_name not in design_cache:
                base_price = _to_decimal(_cell(ws, row, 2)) or Decimal("0")
                storey = _clean_str(_cell(ws, row, 3)) or "Single"
                frontage = _to_decimal(_cell(ws, row, 4)) or Decimal("0")
                depth = _to_decimal(_cell(ws, row, 5)) or Decimal("0")
                gf_sqm = _to_decimal(_cell(ws, row, 6)) or Decimal("0")
                total_sqm = _to_decimal(_cell(ws, row, 7)) or Decimal("0")
                lot_total = _to_decimal(_cell(ws, row, 8)) or Decimal("0")
                squares = _to_int(_cell(ws, row, 9)) or 0
                details = _clean_str(_cell(ws, row, 10))

                design = HouseDesign(
                    brand=brand,
                    house_name=house_name,
                    base_price=base_price,
                    storey=storey,
                    frontage=frontage,
                    depth=depth,
                    gf_sqm=gf_sqm,
                    total_sqm=total_sqm,
                    lot_total_sqm=lot_total,
                    squares=squares,
                    details=details,
                    active=True,
                )
                db.add(design)
                db.flush()
                design_cache[house_name] = design
                result.houses_created += 1
            else:
                design = design_cache[house_name]

            # Create facade record
            facade_name = _clean_str(_cell(ws, row, 11))
            if facade_name:
                if (design.design_id, facade_name) not in facade_cache:
                    raw_price = _cell(ws, row, 12)
                    is_included = False
                    facade_price = Decimal("0")

                    if isinstance(raw_price, str) and raw_price.strip().lower() == "included":
                        is_included = True
                        facade_price = Decimal("0")
                    else:
                        fp = _to_decimal(raw_price)
                        if fp is not None:
                            facade_price = fp
                        else:
                            is_included = True

                    facade_details = _clean_str(_cell(ws, row, 13))

                    facade = HouseFacade(
                        design_id=design.design_id,
                        facade_name=facade_name,
                        facade_price=facade_price,
                        facade_details=facade_details,
                        is_included=is_included,
                    )
                    db.add(facade)
                    facade_cache.add((design.design_id, facade_name))
                    result.facades_created += 1
                else:
                    result.skipped += 1
        except Exception as exc:
            result.errors.append(f"Houses row {row}: {exc}")

        row += 1

    db.flush()
    logger.info(
        "House designs: %d created, %d facades created",
        result.houses_created, result.facades_created,
    )
    return result


# ---------------------------------------------------------------------------
# 2. Energy Ratings
# ---------------------------------------------------------------------------

def _import_energy_ratings(db: Session, ws, brand: str) -> ImportResult:
    """Import energy ratings from Houses sheet (Table12 area).

    Layout (row 3 = headers, data starts row 4, cols R-W / 18-23):
      R=House, S=Garage Side, T=Orientation, U=Updated Star Rating,
      V=Best / Worst, W=Cost
    """
    result = ImportResult()

    # Build lookup: house_name -> design_id
    designs = {d.house_name: d.design_id for d in
               db.query(HouseDesign).filter(HouseDesign.brand == brand).all()}

    # Cache existing ratings
    existing: set[tuple[int, str, str]] = set()
    for er in db.query(EnergyRating).join(HouseDesign).filter(
        HouseDesign.brand == brand
    ).all():
        existing.add((er.design_id, er.garage_side, er.orientation))

    row = 4
    while True:
        house_name = _clean_str(_cell(ws, row, 18))
        if house_name is None:
            if all(_clean_str(_cell(ws, row + i, 18)) is None for i in range(3)):
                break
            row += 1
            result.skipped += 1
            continue

        try:
            design_id = designs.get(house_name)
            if design_id is None:
                result.errors.append(
                    f"Energy row {row}: house '{house_name}' not found in designs"
                )
                row += 1
                continue

            garage_side = _clean_str(_cell(ws, row, 19)) or ""
            orientation = _clean_str(_cell(ws, row, 20)) or ""
            star_rating = _to_decimal(_cell(ws, row, 21)) or Decimal("0")
            best_worst = _clean_str(_cell(ws, row, 22)) or ""
            compliance_cost = _to_decimal(_cell(ws, row, 23)) or Decimal("0")

            key = (design_id, garage_side, orientation)
            if key not in existing:
                er = EnergyRating(
                    design_id=design_id,
                    garage_side=garage_side,
                    orientation=orientation,
                    star_rating=star_rating,
                    best_worst=best_worst,
                    compliance_cost=compliance_cost,
                )
                db.add(er)
                existing.add(key)
                result.energy_ratings_created += 1
            else:
                result.skipped += 1
        except Exception as exc:
            result.errors.append(f"Energy row {row}: {exc}")

        row += 1

    db.flush()
    logger.info("Energy ratings: %d created", result.energy_ratings_created)
    return result


# ---------------------------------------------------------------------------
# 3. FBC Escalation Bands
# ---------------------------------------------------------------------------

def _import_fbc_bands(db: Session, ws, brand: str) -> ImportResult:
    """Import FBC escalation bands from Houses sheet (Table3 area).

    Layout (row 3 = headers, data starts row 4, cols AT-AV / 46-48):
      AT=FBC Day 1, AU=FBC Day 2, AV=%
    """
    result = ImportResult()

    existing = {b.day_start for b in
                db.query(FbcEscalationBand).filter(
                    FbcEscalationBand.brand == brand
                ).all()}

    row = 4
    while True:
        day_start = _to_int(_cell(ws, row, 46))
        if day_start is None:
            break

        try:
            day_end = _to_int(_cell(ws, row, 47)) or day_start
            multiplier = _to_decimal(_cell(ws, row, 48)) or Decimal("1")

            if day_start not in existing:
                band = FbcEscalationBand(
                    brand=brand,
                    day_start=day_start,
                    day_end=day_end,
                    multiplier=multiplier,
                )
                db.add(band)
                existing.add(day_start)
                result.fbc_bands_created += 1
            else:
                result.skipped += 1
        except Exception as exc:
            result.errors.append(f"FBC row {row}: {exc}")

        row += 1

    db.flush()
    logger.info("FBC bands: %d created", result.fbc_bands_created)
    return result


# ---------------------------------------------------------------------------
# 4. Upgrades
# ---------------------------------------------------------------------------

_CATEGORY_PATTERN = re.compile(r"^\*\*\*(.+?)\*\*\*$")


def _import_upgrades(db: Session, ws, brand: str) -> ImportResult:
    """Import upgrades from the Upgrades sheet (Table4 area).

    Layout (row 1 = headers, data starts row 2):
      A=Date added, B=Hermitage Homes - Upgrades (description),
      C=$$ (price), D=Notes

    Category separator rows contain ***CATEGORY_NAME***.
    """
    result = ImportResult()

    # Cache existing categories
    cat_cache: dict[str, UpgradeCategory] = {}
    for cat in db.query(UpgradeCategory).filter(
        UpgradeCategory.brand == brand
    ).all():
        cat_cache[cat.name] = cat

    # Cache existing upgrades by description
    existing_descriptions: set[str] = set()
    for ui in db.query(UpgradeItem).filter(UpgradeItem.brand == brand).all():
        existing_descriptions.add(ui.description)

    current_category: UpgradeCategory | None = None
    category_order = 0
    item_order = 0

    row = 2  # skip header row
    while True:
        desc = _clean_str(_cell(ws, row, 2))
        if desc is None:
            if all(_clean_str(_cell(ws, row + i, 2)) is None for i in range(3)):
                break
            row += 1
            continue

        try:
            # Check if this is a category separator
            match = _CATEGORY_PATTERN.match(desc)
            if match:
                cat_name = match.group(1).strip()
                if cat_name not in cat_cache:
                    category_order += 1
                    cat = UpgradeCategory(
                        brand=brand,
                        name=cat_name,
                        sort_order=category_order,
                    )
                    db.add(cat)
                    db.flush()
                    cat_cache[cat_name] = cat
                    result.upgrade_categories_created += 1
                current_category = cat_cache[cat_name]
                item_order = 0
                row += 1
                continue

            # Normal upgrade item
            if desc not in existing_descriptions:
                price = _to_decimal(_cell(ws, row, 3)) or Decimal("0")
                date_added = _to_date(_cell(ws, row, 1))
                notes = _clean_str(_cell(ws, row, 4))
                item_order += 1

                item = UpgradeItem(
                    brand=brand,
                    category_id=current_category.category_id if current_category else None,
                    description=desc,
                    price=price,
                    date_added=date_added,
                    notes=notes,
                    sort_order=item_order,
                )
                db.add(item)
                existing_descriptions.add(desc)
                result.upgrades_created += 1
            else:
                result.skipped += 1
        except Exception as exc:
            result.errors.append(f"Upgrades row {row}: {exc}")

        row += 1

    db.flush()
    logger.info(
        "Upgrades: %d categories, %d items created",
        result.upgrade_categories_created, result.upgrades_created,
    )
    return result


# ---------------------------------------------------------------------------
# 5. Estate Design Guidelines
# ---------------------------------------------------------------------------

# Short names for the 27 guideline columns (J=10 through AJ=36)
_GUIDELINE_SHORT_NAMES = {
    10: "recycled_water",
    11: "fibre_optic",
    12: "eaves_1500",
    13: "eaves_3000",
    14: "water_tank_2000_garden",
    15: "water_tank_2000_toilets",
    16: "water_tank_5000_toilets",
    17: "timber_fencing_additional",
    18: "timber_fencing_capping",
    19: "colourbond_fencing",
    20: "timber_fencing_exposed_125x125",
    21: "timber_fencing_exposed_125x75",
    22: "roof_pitch_25deg",
    23: "colorbond_roofing",
    24: "flat_roof_tiles_cat3",
    25: "colour_through_concrete",
    26: "corner_treatment",
    27: "brickwork_above_garage",
    28: "brickwork_above_windows",
    29: "exposed_aggregate_concrete",
    30: "ceiling_2590mm",
    31: "ceiling_2720mm",
    32: "rendered_front_projection",
    33: "rendered_whole_facade",
    34: "travel_surcharge",
    35: "advanced_trees_landscaping",
    36: "single_crossover_footpath",
}


def _import_estates_and_guidelines(db: Session, ws, brand: str) -> ImportResult:
    """Import estate design guidelines from ESTATES sheet.

    Layout (row 10 = headers, data starts row 11):
      A=Estate, B=Stage, C=Suburb, ...
      J-AJ (cols 10-36): 27 design guideline columns

    Creates GuidelineType records from headers, then creates
    EstateDesignGuideline records for non-null cells.
    Only links to existing estates in the DB.
    """
    result = ImportResult()

    # 1. Create/get guideline types from column headers
    type_cache: dict[str, GuidelineType] = {}
    for gt in db.query(GuidelineType).all():
        type_cache[gt.short_name] = gt

    for col_idx, short_name in _GUIDELINE_SHORT_NAMES.items():
        if short_name not in type_cache:
            full_desc = _clean_str(_cell(ws, 10, col_idx)) or short_name
            gt = GuidelineType(
                short_name=short_name,
                description=full_desc,
                sort_order=col_idx - 9,
            )
            db.add(gt)
            db.flush()
            type_cache[short_name] = gt
            result.guideline_types_created += 1

    # 2. Build estate lookup: estate_name -> estate_id
    estate_lookup: dict[str, int] = {}
    for e in db.query(Estate).all():
        estate_lookup[e.estate_name] = e.estate_id

    # Build stage lookup: (estate_id, stage_name) -> stage_id
    stage_lookup: dict[tuple[int, str], int] = {}
    for s in db.query(EstateStage).all():
        stage_lookup[(s.estate_id, s.name)] = s.stage_id

    # Existing guidelines cache
    existing_guidelines: set[tuple[int, int | None, int]] = set()
    for eg in db.query(EstateDesignGuideline).all():
        existing_guidelines.add((eg.estate_id, eg.stage_id, eg.type_id))

    estates_not_found: set[str] = set()

    row = 11
    while True:
        estate_name = _clean_str(_cell(ws, row, 1))
        if estate_name is None:
            if all(_clean_str(_cell(ws, row + i, 1)) is None for i in range(5)):
                break
            row += 1
            result.skipped += 1
            continue

        try:
            estate_id = estate_lookup.get(estate_name)
            if estate_id is None:
                if estate_name not in estates_not_found:
                    estates_not_found.add(estate_name)
                row += 1
                result.skipped += 1
                continue

            # Resolve stage
            stage_val = _clean_str(str(_cell(ws, row, 2)) if _cell(ws, row, 2) is not None else "")
            stage_id = None
            if stage_val:
                stage_id = stage_lookup.get((estate_id, stage_val))

            # Process each guideline column
            for col_idx, short_name in _GUIDELINE_SHORT_NAMES.items():
                cell_val = _cell(ws, row, col_idx)
                if cell_val is None:
                    continue

                gt = type_cache[short_name]
                key = (estate_id, stage_id, gt.type_id)
                if key in existing_guidelines:
                    continue

                # Determine if it's a cost or text override
                cost = _to_decimal(cell_val)
                override_text = None
                if cost is None:
                    # It's a text value
                    override_text = _clean_str(cell_val)
                    if override_text is None:
                        continue

                edg = EstateDesignGuideline(
                    estate_id=estate_id,
                    stage_id=stage_id,
                    type_id=gt.type_id,
                    cost=cost,
                    override_text=override_text,
                )
                db.add(edg)
                existing_guidelines.add(key)
                result.estate_guidelines_created += 1

        except Exception as exc:
            result.errors.append(f"ESTATES row {row}: {exc}")

        row += 1

    if estates_not_found:
        result.errors.append(
            f"Skipped guidelines for {len(estates_not_found)} estates not found in DB"
        )

    db.flush()
    logger.info(
        "Guidelines: %d types, %d estate guidelines created",
        result.guideline_types_created, result.estate_guidelines_created,
    )
    return result


# ---------------------------------------------------------------------------
# 6. Travel Surcharges
# ---------------------------------------------------------------------------

def _import_travel_surcharges(db: Session, ws) -> ImportResult:
    """Import travel surcharges from the ESTATES sheet (Table5 area).

    Layout (row 10 = headers, data starts row 11, cols AO-AQ / 41-43):
      AO=Travel Surcharge (suburb + postcode), AP=$$, AQ=Region
    """
    result = ImportResult()

    existing: dict[str, TravelSurcharge] = {}
    for ts in db.query(TravelSurcharge).all():
        existing[ts.suburb_name] = ts

    row = 11
    while True:
        raw_suburb = _clean_str(_cell(ws, row, 41))
        if raw_suburb is None:
            if all(_clean_str(_cell(ws, row + i, 41)) is None for i in range(3)):
                break
            row += 1
            continue

        try:
            # Parse suburb name and postcode from "Armstrong Creek 3217"
            # Use the full string as suburb_name (unique constraint is on
            # suburb_name alone) so "Bakery Hill 3350" and "Bakery Hill 3354"
            # are treated as separate entries.
            parts = raw_suburb.rsplit(" ", 1)
            postcode = None
            suburb_name = raw_suburb  # keep full string as the unique name
            if len(parts) == 2 and parts[1].isdigit() and len(parts[1]) == 4:
                postcode = parts[1]

            amount = _to_decimal(_cell(ws, row, 42)) or Decimal("0")
            region = _clean_str(_cell(ws, row, 43))

            if suburb_name not in existing:
                ts = TravelSurcharge(
                    suburb_name=suburb_name,
                    postcode=postcode,
                    surcharge_amount=amount,
                    region_name=region,
                )
                db.add(ts)
                existing[suburb_name] = ts
                result.travel_surcharges_created += 1
            else:
                result.skipped += 1
        except Exception as exc:
            result.errors.append(f"Travel surcharge row {row}: {exc}")

        row += 1

    db.flush()
    logger.info("Travel surcharges: %d created", result.travel_surcharges_created)
    return result


# ---------------------------------------------------------------------------
# 7. Site Costs
# ---------------------------------------------------------------------------

_TIER_DEFS = [
    {"name": "0-1000mm", "fall_min": 0, "fall_max": 1000,
     "header_row": 84, "data_start": 87, "data_end": 94},
    {"name": "1001-1500mm", "fall_min": 1001, "fall_max": 1500,
     "header_row": 96, "data_start": 99, "data_end": 107},
    {"name": "1501-2000mm", "fall_min": 1501, "fall_max": 2000,
     "header_row": 109, "data_start": 112, "data_end": 121},
]


def _import_site_costs(db: Session, ws) -> ImportResult:
    """Import site costs from the Site Costs sheet.

    Three tiers with line items, plus basic site costs (rows 17-83)
    and postcode rock removal costs (cols J-K, rows 22-78).
    """
    result = ImportResult()

    # --- Postcode rock removal costs (cols J=10, K=11, rows 22-78) ---
    existing_postcodes: set[str] = {p.postcode for p in db.query(PostcodeSiteCost).all()}
    for row in range(22, 79):
        pc_val = _cell(ws, row, 10)
        cost_val = _cell(ws, row, 11)
        if pc_val is None:
            continue
        try:
            postcode = str(int(pc_val))
            cost = _to_decimal(cost_val) or Decimal("0")
            if postcode not in existing_postcodes:
                db.add(PostcodeSiteCost(postcode=postcode, rock_removal_cost=cost))
                existing_postcodes.add(postcode)
                result.postcode_costs_created += 1
        except Exception as exc:
            result.errors.append(f"Postcode row {row}: {exc}")

    # --- Basic site cost items (rows 17-83, not tiered) ---
    # These go into site_cost_items with tier_id=None
    basic_items = [
        (18, "H2 waffle foundation"),
        (19, "Minimum piering"),
        (20, "Soil removal & fill import"),
        (80, "Front retaining walls"),
        (81, "Second soil test & re-estab survey"),
        (82, "Manual handling - restricted site"),
        (83, "Services & connections under 650m2"),
    ]

    existing_item_names: set[tuple[int | None, str]] = set()
    for si in db.query(SiteCostItem).all():
        existing_item_names.add((si.tier_id, si.item_name))

    for row_num, item_name in basic_items:
        if (None, item_name) in existing_item_names:
            result.skipped += 1
            continue
        try:
            single_cost = _to_decimal(_cell(ws, row_num, 4))
            double_cost = _to_decimal(_cell(ws, row_num, 5))
            description = _clean_str(_cell(ws, row_num, 6)) or item_name

            item = SiteCostItem(
                tier_id=None,
                item_name=item_name,
                condition_type="basic",
                condition_description=description,
                cost_single_lt190=single_cost,
                cost_double_lt190=double_cost,
                cost_single_191_249=single_cost,
                cost_double_191_249=double_cost,
                cost_single_250_300=single_cost,
                cost_double_250_300=double_cost,
                cost_single_300plus=single_cost,
                cost_double_300plus=double_cost,
                sort_order=row_num,
            )
            db.add(item)
            existing_item_names.add((None, item_name))
            result.site_cost_items_created += 1
        except Exception as exc:
            result.errors.append(f"Basic site cost row {row_num}: {exc}")

    # --- Tiered site costs ---
    tier_cache: dict[str, SiteCostTier] = {}
    for t in db.query(SiteCostTier).all():
        tier_cache[t.tier_name] = t

    for tier_def in _TIER_DEFS:
        tier_name = tier_def["name"]
        if tier_name not in tier_cache:
            tier = SiteCostTier(
                tier_name=tier_name,
                fall_min_mm=tier_def["fall_min"],
                fall_max_mm=tier_def["fall_max"],
            )
            db.add(tier)
            db.flush()
            tier_cache[tier_name] = tier
            result.site_cost_tiers_created += 1

        tier = tier_cache[tier_name]

        for row_num in range(tier_def["data_start"], tier_def["data_end"] + 1):
            item_name = _clean_str(_cell(ws, row_num, 1))
            if not item_name:
                continue

            if (tier.tier_id, item_name) in existing_item_names:
                result.skipped += 1
                continue

            try:
                # 8 size-banded cost columns at cols J-S (10-19 -> mapped to
                # single_lt190 through double_300plus):
                # col 10=Single, 11=Double (default/summary)
                # col 12=Single<190, 13=Double<190, 14=Single 191-249, 15=Double 191-249
                # col 16=Single 250-300, 17=Double 250-300, 18=Single 300+, 19=Double 300+
                c_s_lt190 = _to_decimal(_cell(ws, row_num, 12)) or _to_decimal(_cell(ws, row_num, 10))
                c_d_lt190 = _to_decimal(_cell(ws, row_num, 13)) or _to_decimal(_cell(ws, row_num, 11))
                c_s_191 = _to_decimal(_cell(ws, row_num, 14)) or c_s_lt190
                c_d_191 = _to_decimal(_cell(ws, row_num, 15)) or c_d_lt190
                c_s_250 = _to_decimal(_cell(ws, row_num, 16)) or c_s_lt190
                c_d_250 = _to_decimal(_cell(ws, row_num, 17)) or c_d_lt190
                c_s_300 = _to_decimal(_cell(ws, row_num, 18)) or c_s_lt190
                c_d_300 = _to_decimal(_cell(ws, row_num, 19)) or c_d_lt190

                item = SiteCostItem(
                    tier_id=tier.tier_id,
                    item_name=item_name,
                    condition_type="tiered",
                    condition_description=None,
                    cost_single_lt190=c_s_lt190,
                    cost_double_lt190=c_d_lt190,
                    cost_single_191_249=c_s_191,
                    cost_double_191_249=c_d_191,
                    cost_single_250_300=c_s_250,
                    cost_double_250_300=c_d_250,
                    cost_single_300plus=c_s_300,
                    cost_double_300plus=c_d_300,
                    sort_order=row_num,
                )
                db.add(item)
                existing_item_names.add((tier.tier_id, item_name))
                result.site_cost_items_created += 1
            except Exception as exc:
                result.errors.append(f"Site cost tier '{tier_name}' row {row_num}: {exc}")

    db.flush()
    logger.info(
        "Site costs: %d tiers, %d items, %d postcode costs created",
        result.site_cost_tiers_created, result.site_cost_items_created,
        result.postcode_costs_created,
    )
    return result


# ---------------------------------------------------------------------------
# 8. Commissions (GROUPS sheet)
# ---------------------------------------------------------------------------

# BDM tables: (name_col, comms_col, pct_col, gst_col)
_BDM_TABLE_COLS = [
    (3, 4, 5, 6),      # Bec
    (8, 9, 10, 11),     # Layal
    (13, 14, 15, 16),   # Simone
    (18, 19, 20, 21),   # Caitlin
    (23, 24, 25, 26),   # Josh
    (28, 29, 30, 31),   # Peter
    (33, 34, 35, 36),   # William
    (38, 39, 40, 41),   # Vattey
    (43, 44, 45, 46),   # Matthew
]


def _import_commissions(db: Session, ws, brand: str) -> ImportResult:
    """Import wholesale groups and BDM commission rates from the GROUPS sheet.

    Layout: row 2 has BDM name headers in specific columns.
    Each BDM has a 4-column block: group name, comms inc GST, comms %, GST flag.
    Data starts row 3.
    """
    result = ImportResult()

    # Cache wholesale groups
    group_cache: dict[str, WholesaleGroup] = {}
    for wg in db.query(WholesaleGroup).all():
        group_cache[wg.group_name] = wg

    # Build BDM profile lookup by first name
    profile_lookup: dict[str, int] = {}
    for p in db.query(Profile).all():
        profile_lookup[p.first_name.lower()] = p.profile_id

    # Cache existing commission rates
    existing_rates: set[tuple[int, int]] = set()
    for cr in db.query(CommissionRate).all():
        existing_rates.add((cr.bdm_profile_id, cr.group_id))

    for name_col, comms_col, pct_col, gst_col in _BDM_TABLE_COLS:
        bdm_name = _clean_str(_cell(ws, 2, name_col))
        if not bdm_name:
            continue

        bdm_profile_id = profile_lookup.get(bdm_name.lower())
        if bdm_profile_id is None:
            result.errors.append(
                f"BDM '{bdm_name}' not found in profiles table, skipping commission rates"
            )

        row = 3
        while True:
            group_name = _clean_str(_cell(ws, row, name_col))
            if group_name is None:
                if all(_clean_str(_cell(ws, row + i, name_col)) is None for i in range(3)):
                    break
                row += 1
                continue

            try:
                # Get or create wholesale group
                if group_name not in group_cache:
                    gst_val = _clean_str(_cell(ws, row, gst_col))
                    gst_registered = gst_val is not None and gst_val.lower() in (
                        "yes", "y", "true", "1",
                    )
                    wg = WholesaleGroup(
                        group_name=group_name,
                        gst_registered=gst_registered,
                        active=True,
                    )
                    db.add(wg)
                    db.flush()
                    group_cache[group_name] = wg
                    result.wholesale_groups_created += 1

                # Create commission rate if BDM exists
                if bdm_profile_id is not None:
                    wg = group_cache[group_name]
                    key = (bdm_profile_id, wg.group_id)
                    if key not in existing_rates:
                        comm_fixed = _to_decimal(_cell(ws, row, comms_col))
                        comm_pct = _to_decimal(_cell(ws, row, pct_col))

                        cr = CommissionRate(
                            bdm_profile_id=bdm_profile_id,
                            group_id=wg.group_id,
                            commission_fixed=comm_fixed,
                            commission_pct=comm_pct,
                            brand=brand,
                        )
                        db.add(cr)
                        existing_rates.add(key)
                        result.commission_rates_created += 1
                    else:
                        result.skipped += 1
            except Exception as exc:
                result.errors.append(
                    f"GROUPS BDM '{bdm_name}' row {row}: {exc}"
                )

            row += 1

    db.flush()
    logger.info(
        "Commissions: %d wholesale groups, %d rates created",
        result.wholesale_groups_created, result.commission_rates_created,
    )
    return result


# ---------------------------------------------------------------------------
# Master Import
# ---------------------------------------------------------------------------

def import_from_excel(
    db: Session,
    workbook_path: str,
    brand: str = "Hermitage Homes",
) -> ImportResult:
    """Master import function.

    Reads all pricing data from the Hermitage Homes Excel workbook and
    populates the 14 new pricing engine tables. Idempotent and error-tolerant.

    The caller is responsible for calling ``db.commit()`` on success.
    """
    result = ImportResult()

    logger.info("Loading workbook: %s", workbook_path)
    wb = openpyxl.load_workbook(workbook_path, data_only=True, read_only=False)

    try:
        # Houses sheet: designs, facades, energy ratings, FBC bands
        ws_houses = wb["Houses"]
        logger.info("Importing house designs...")
        result.merge(_import_house_designs(db, ws_houses, brand))

        logger.info("Importing energy ratings...")
        result.merge(_import_energy_ratings(db, ws_houses, brand))

        logger.info("Importing FBC escalation bands...")
        result.merge(_import_fbc_bands(db, ws_houses, brand))

        # Upgrades sheet
        ws_upgrades = wb["Upgrades"]
        logger.info("Importing upgrades...")
        result.merge(_import_upgrades(db, ws_upgrades, brand))

        # ESTATES sheet: guidelines, travel surcharges
        ws_estates = wb["ESTATES"]
        logger.info("Importing guideline types and estate guidelines...")
        result.merge(_import_estates_and_guidelines(db, ws_estates, brand))

        logger.info("Importing travel surcharges...")
        result.merge(_import_travel_surcharges(db, ws_estates))

        # Site Costs sheet
        ws_site_costs = wb["Site Costs"]
        logger.info("Importing site costs...")
        result.merge(_import_site_costs(db, ws_site_costs))

        # GROUPS sheet: commissions
        ws_groups = wb["GROUPS"]
        logger.info("Importing commissions...")
        result.merge(_import_commissions(db, ws_groups, brand))

    finally:
        wb.close()

    logger.info(
        "Import complete: %d houses, %d facades, %d energy ratings, "
        "%d upgrades, %d FBC bands, %d guideline types, %d estate guidelines, "
        "%d travel surcharges, %d site cost items, %d postcode costs, "
        "%d wholesale groups, %d commission rates, %d skipped, %d errors",
        result.houses_created, result.facades_created,
        result.energy_ratings_created, result.upgrades_created,
        result.fbc_bands_created, result.guideline_types_created,
        result.estate_guidelines_created, result.travel_surcharges_created,
        result.site_cost_items_created, result.postcode_costs_created,
        result.wholesale_groups_created, result.commission_rates_created,
        result.skipped, len(result.errors),
    )
    return result

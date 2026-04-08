"""Extract pricing data from the Hermitage Homes Excel workbook to CSV files.

Usage:
    python scripts/extract_pricing_to_csv.py
    python scripts/extract_pricing_to_csv.py --workbook "Reference/Pricing sheet 2026.xlsm"
    python scripts/extract_pricing_to_csv.py --brand "Kingsbridge Homes"

Outputs 14 CSV files to data/seed/.
"""

from __future__ import annotations

import csv
import os
import re
import sys
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

import openpyxl

# ---------------------------------------------------------------------------
# Helpers (reused from import_pricing_workbook.py)
# ---------------------------------------------------------------------------

def _clean_str(val: Any) -> str | None:
    if val is None:
        return None
    s = str(val).strip()
    s = s.replace("\u2018", "'").replace("\u2019", "'")
    s = s.replace("\u201c", '"').replace("\u201d", '"')
    if not s:
        return None
    return s


def _to_decimal(val: Any) -> Decimal | None:
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
    if val is None:
        return None
    if isinstance(val, bool):
        return None
    try:
        return int(float(val))
    except (ValueError, TypeError):
        return None


def _to_date(val: Any) -> date | None:
    if val is None:
        return None
    if isinstance(val, datetime):
        return val.date()
    if isinstance(val, date):
        return val
    return None


def _cell(ws, row: int, col: int) -> Any:
    return ws.cell(row, col).value


def _gap_break(ws, row: int, col: int, gap: int = 3) -> bool:
    """Return True if the next `gap` rows at `col` are all blank."""
    return all(_clean_str(_cell(ws, row + i, col)) is None for i in range(gap))


# ---------------------------------------------------------------------------
# CSV writer helper
# ---------------------------------------------------------------------------

def _open_csv(path: str, headers: list[str]):
    """Open a CSV file for writing and return (file_handle, csv_writer)."""
    fh = open(path, "w", newline="", encoding="utf-8")
    writer = csv.writer(fh)
    writer.writerow(headers)
    return fh, writer


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_CATEGORY_PATTERN = re.compile(r"^\*\*\*(.+?)\*\*\*$")

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

_GUIDELINE_CATEGORY_NAMES = {
    "recycled_water": "3rd Pipe Recycled Water",
    "fibre_optic": "Fibre Optic",
    "eaves_1500": "Eaves 450mm (1500mm Projection)",
    "eaves_3000": "Eaves 450mm (3000mm Projection)",
    "water_tank_2000_garden": "2000L Water Tank (Garden)",
    "water_tank_2000_toilets": "2000L Water Tank (Toilets)",
    "water_tank_5000_toilets": "5000L Water Tank (Toilets)",
    "timber_fencing_additional": "Timber Fencing Additional",
    "timber_fencing_capping": "Timber Fencing Capping",
    "colourbond_fencing": "Colorbond Fencing",
    "timber_fencing_exposed_125x125": "Timber Fencing Exposed 125x125",
    "timber_fencing_exposed_125x75": "Timber Fencing Exposed 125x75",
    "roof_pitch_25deg": "Roof Pitch 25 Degrees",
    "colorbond_roofing": "Colorbond Roofing",
    "flat_roof_tiles_cat3": "Flat Roof Tiles Cat 3",
    "colour_through_concrete": "Colour Through Concrete",
    "corner_treatment": "Corner Treatment",
    "brickwork_above_garage": "Brickwork Above Garage",
    "brickwork_above_windows": "Brickwork Above Windows",
    "exposed_aggregate_concrete": "Exposed Aggregate Concrete",
    "ceiling_2590mm": "Ceiling Height 2590mm",
    "ceiling_2720mm": "Ceiling Height 2720mm",
    "rendered_front_projection": "Rendered Front Projection",
    "rendered_whole_facade": "Rendered Whole Facade",
    "travel_surcharge": "Travel Surcharge",
    "advanced_trees_landscaping": "Advanced Trees & Landscaping",
    "single_crossover_footpath": "Single Crossover & Footpath",
}

_BDM_TABLE_COLS = [
    (3, 4, 5, 6),
    (8, 9, 10, 11),
    (13, 14, 15, 16),
    (18, 19, 20, 21),
    (23, 24, 25, 26),
    (28, 29, 30, 31),
    (33, 34, 35, 36),
    (38, 39, 40, 41),
    (43, 44, 45, 46),
]

_TIER_DEFS = [
    {"name": "0-1000mm", "fall_min": 0, "fall_max": 1000,
     "header_row": 84, "data_start": 87, "data_end": 94},
    {"name": "1001-1500mm", "fall_min": 1001, "fall_max": 1500,
     "header_row": 96, "data_start": 99, "data_end": 107},
    {"name": "1501-2000mm", "fall_min": 1501, "fall_max": 2000,
     "header_row": 109, "data_start": 112, "data_end": 121},
]

_BASIC_ITEMS = [
    (18, "H2 waffle foundation"),
    (19, "Minimum piering"),
    (20, "Soil removal & fill import"),
    (80, "Front retaining walls"),
    (81, "Second soil test & re-estab survey"),
    (82, "Manual handling - restricted site"),
    (83, "Services & connections under 650m2"),
]


# ---------------------------------------------------------------------------
# Extraction functions
# ---------------------------------------------------------------------------

def _fmt(val: Any) -> str:
    """Format a value for CSV output."""
    if val is None:
        return ""
    if isinstance(val, Decimal):
        # Remove trailing zeros but keep at least one decimal if needed
        return str(val)
    if isinstance(val, bool):
        return str(val)
    if isinstance(val, date):
        return val.isoformat()
    return str(val)


def extract_house_designs(ws, brand: str, out_dir: str) -> int:
    """Extract house_designs.csv"""
    path = os.path.join(out_dir, "house_designs.csv")
    fh, writer = _open_csv(path, [
        "brand", "house_name", "base_price", "storey", "frontage", "depth",
        "gf_sqm", "total_sqm", "lot_total_sqm", "squares", "details",
    ])
    count = 0
    seen = set()
    row = 4
    while True:
        house_name = _clean_str(_cell(ws, row, 1))
        if house_name is None:
            if _gap_break(ws, row, 1):
                break
            row += 1
            continue

        if house_name not in seen:
            seen.add(house_name)
            writer.writerow([
                brand,
                house_name,
                _fmt(_to_decimal(_cell(ws, row, 2)) or Decimal("0")),
                _fmt(_clean_str(_cell(ws, row, 3)) or "Single"),
                _fmt(_to_decimal(_cell(ws, row, 4)) or Decimal("0")),
                _fmt(_to_decimal(_cell(ws, row, 5)) or Decimal("0")),
                _fmt(_to_decimal(_cell(ws, row, 6)) or Decimal("0")),
                _fmt(_to_decimal(_cell(ws, row, 7)) or Decimal("0")),
                _fmt(_to_decimal(_cell(ws, row, 8)) or Decimal("0")),
                _fmt(_to_int(_cell(ws, row, 9)) or 0),
                _fmt(_clean_str(_cell(ws, row, 10))),
            ])
            count += 1
        row += 1

    fh.close()
    return count


def extract_house_facades(ws, brand: str, out_dir: str) -> int:
    """Extract house_facades.csv"""
    path = os.path.join(out_dir, "house_facades.csv")
    fh, writer = _open_csv(path, [
        "brand", "house_name", "facade_name", "facade_price", "facade_details",
        "is_included",
    ])
    count = 0
    current_house = None
    row = 4
    while True:
        house_name = _clean_str(_cell(ws, row, 1))
        if house_name is None and current_house is None:
            if _gap_break(ws, row, 1) and _gap_break(ws, row, 11):
                break
            row += 1
            continue

        if house_name is not None:
            current_house = house_name

        facade_name = _clean_str(_cell(ws, row, 11))
        if facade_name and current_house:
            raw_price = _cell(ws, row, 12)
            is_included = False
            facade_price = Decimal("0")

            if isinstance(raw_price, str) and raw_price.strip().lower() == "included":
                is_included = True
            else:
                fp = _to_decimal(raw_price)
                if fp is not None:
                    facade_price = fp
                else:
                    is_included = True

            facade_details = _clean_str(_cell(ws, row, 13))

            writer.writerow([
                brand,
                current_house,
                facade_name,
                _fmt(facade_price),
                _fmt(facade_details),
                is_included,
            ])
            count += 1

        # Reset current_house tracking on gap
        if house_name is None and _gap_break(ws, row, 1):
            if _gap_break(ws, row, 11):
                break

        row += 1

    fh.close()
    return count


def extract_energy_ratings(ws, brand: str, out_dir: str) -> int:
    """Extract energy_ratings.csv"""
    path = os.path.join(out_dir, "energy_ratings.csv")
    fh, writer = _open_csv(path, [
        "brand", "house_name", "garage_side", "orientation", "star_rating",
        "best_worst", "compliance_cost",
    ])
    count = 0
    row = 4
    while True:
        house_name = _clean_str(_cell(ws, row, 18))
        if house_name is None:
            if _gap_break(ws, row, 18):
                break
            row += 1
            continue

        writer.writerow([
            brand,
            house_name,
            _fmt(_clean_str(_cell(ws, row, 19)) or ""),
            _fmt(_clean_str(_cell(ws, row, 20)) or ""),
            _fmt(_to_decimal(_cell(ws, row, 21)) or Decimal("0")),
            _fmt(_clean_str(_cell(ws, row, 22)) or ""),
            _fmt(_to_decimal(_cell(ws, row, 23)) or Decimal("0")),
        ])
        count += 1
        row += 1

    fh.close()
    return count


def extract_fbc_bands(ws, brand: str, out_dir: str) -> int:
    """Extract fbc_escalation_bands.csv"""
    path = os.path.join(out_dir, "fbc_escalation_bands.csv")
    fh, writer = _open_csv(path, [
        "brand", "day_start", "day_end", "multiplier",
    ])
    count = 0
    row = 4
    while True:
        day_start = _to_int(_cell(ws, row, 46))
        if day_start is None:
            break
        day_end = _to_int(_cell(ws, row, 47)) or day_start
        multiplier = _to_decimal(_cell(ws, row, 48)) or Decimal("1")
        writer.writerow([brand, day_start, day_end, _fmt(multiplier)])
        count += 1
        row += 1

    fh.close()
    return count


def extract_upgrades(ws, brand: str, out_dir: str) -> tuple[int, int]:
    """Extract upgrade_categories.csv and upgrade_items.csv.
    Returns (category_count, item_count).
    """
    cat_path = os.path.join(out_dir, "upgrade_categories.csv")
    item_path = os.path.join(out_dir, "upgrade_items.csv")

    cat_fh, cat_writer = _open_csv(cat_path, ["brand", "name", "sort_order"])
    item_fh, item_writer = _open_csv(item_path, [
        "brand", "category_name", "description", "price", "date_added",
        "notes", "sort_order",
    ])

    cat_count = 0
    item_count = 0
    current_category = None
    category_order = 0
    item_order = 0

    row = 2
    while True:
        desc = _clean_str(_cell(ws, row, 2))
        if desc is None:
            if _gap_break(ws, row, 2):
                break
            row += 1
            continue

        match = _CATEGORY_PATTERN.match(desc)
        if match:
            cat_name = match.group(1).strip()
            category_order += 1
            cat_writer.writerow([brand, cat_name, category_order])
            current_category = cat_name
            item_order = 0
            cat_count += 1
        else:
            price = _to_decimal(_cell(ws, row, 3)) or Decimal("0")
            date_added = _to_date(_cell(ws, row, 1))
            notes = _clean_str(_cell(ws, row, 4))
            item_order += 1

            item_writer.writerow([
                brand,
                _fmt(current_category),
                desc,
                _fmt(price),
                _fmt(date_added),
                _fmt(notes),
                item_order,
            ])
            item_count += 1

        row += 1

    cat_fh.close()
    item_fh.close()
    return cat_count, item_count


def extract_wholesale_groups_and_commissions(ws, brand: str, out_dir: str) -> tuple[int, int]:
    """Extract wholesale_groups.csv and commission_rates.csv.
    Returns (group_count, rate_count).
    """
    grp_path = os.path.join(out_dir, "wholesale_groups.csv")
    comm_path = os.path.join(out_dir, "commission_rates.csv")

    grp_fh, grp_writer = _open_csv(grp_path, [
        "group_name", "gst_registered", "active",
    ])
    comm_fh, comm_writer = _open_csv(comm_path, [
        "brand", "bdm_name", "group_name", "commission_fixed", "commission_pct",
    ])

    group_cache: dict[str, bool] = {}  # group_name -> gst_registered
    grp_count = 0
    comm_count = 0

    for name_col, comms_col, pct_col, gst_col in _BDM_TABLE_COLS:
        bdm_name = _clean_str(_cell(ws, 2, name_col))
        if not bdm_name:
            continue

        row = 3
        while True:
            group_name = _clean_str(_cell(ws, row, name_col))
            if group_name is None:
                if _gap_break(ws, row, name_col):
                    break
                row += 1
                continue

            # Track wholesale group (deduplicate across BDM blocks)
            if group_name not in group_cache:
                gst_val = _clean_str(_cell(ws, row, gst_col))
                gst_registered = gst_val is not None and gst_val.lower() in (
                    "yes", "y", "true", "1",
                )
                group_cache[group_name] = gst_registered

            # Commission rate
            comm_fixed = _to_decimal(_cell(ws, row, comms_col))
            comm_pct = _to_decimal(_cell(ws, row, pct_col))

            comm_writer.writerow([
                brand,
                bdm_name,
                group_name,
                _fmt(comm_fixed),
                _fmt(comm_pct),
            ])
            comm_count += 1
            row += 1

    # Write deduplicated groups
    for gname, gst in sorted(group_cache.items()):
        grp_writer.writerow([gname, gst, True])
        grp_count += 1

    grp_fh.close()
    comm_fh.close()
    return grp_count, comm_count


def extract_travel_surcharges(ws, out_dir: str) -> int:
    """Extract travel_surcharges.csv"""
    path = os.path.join(out_dir, "travel_surcharges.csv")
    fh, writer = _open_csv(path, [
        "suburb_name", "postcode", "surcharge_amount", "region_name",
    ])
    count = 0
    row = 11
    while True:
        raw_suburb = _clean_str(_cell(ws, row, 41))
        if raw_suburb is None:
            if _gap_break(ws, row, 41):
                break
            row += 1
            continue

        parts = raw_suburb.rsplit(" ", 1)
        postcode = ""
        suburb_name = raw_suburb
        if len(parts) == 2 and parts[1].isdigit() and len(parts[1]) == 4:
            postcode = parts[1]

        amount = _to_decimal(_cell(ws, row, 42)) or Decimal("0")
        region = _clean_str(_cell(ws, row, 43))

        writer.writerow([suburb_name, postcode, _fmt(amount), _fmt(region)])
        count += 1
        row += 1

    fh.close()
    return count


def extract_postcode_site_costs(ws, out_dir: str) -> int:
    """Extract postcode_site_costs.csv"""
    path = os.path.join(out_dir, "postcode_site_costs.csv")
    fh, writer = _open_csv(path, ["postcode", "rock_removal_cost"])
    count = 0
    for row in range(22, 79):
        pc_val = _cell(ws, row, 10)
        cost_val = _cell(ws, row, 11)
        if pc_val is None:
            continue
        try:
            postcode = str(int(pc_val))
            cost = _to_decimal(cost_val) or Decimal("0")
            writer.writerow([postcode, _fmt(cost)])
            count += 1
        except (ValueError, TypeError):
            pass

    fh.close()
    return count


def extract_site_cost_tiers(out_dir: str) -> int:
    """Extract site_cost_tiers.csv (fixed data)."""
    path = os.path.join(out_dir, "site_cost_tiers.csv")
    fh, writer = _open_csv(path, ["tier_name", "fall_min_mm", "fall_max_mm"])
    for td in _TIER_DEFS:
        writer.writerow([td["name"], td["fall_min"], td["fall_max"]])
    fh.close()
    return len(_TIER_DEFS)


def extract_site_cost_items(ws, out_dir: str) -> int:
    """Extract site_cost_items.csv"""
    path = os.path.join(out_dir, "site_cost_items.csv")
    fh, writer = _open_csv(path, [
        "tier_name", "item_name", "condition_type", "condition_description",
        "cost_single_lt190", "cost_double_lt190",
        "cost_single_191_249", "cost_double_191_249",
        "cost_single_250_300", "cost_double_250_300",
        "cost_single_300plus", "cost_double_300plus",
        "sort_order",
    ])
    count = 0

    # Basic items (no tier)
    for row_num, item_name in _BASIC_ITEMS:
        single_cost = _to_decimal(_cell(ws, row_num, 4))
        double_cost = _to_decimal(_cell(ws, row_num, 5))
        description = _clean_str(_cell(ws, row_num, 6)) or item_name

        writer.writerow([
            "",  # tier_name = None for basic items
            item_name,
            "basic",
            description,
            _fmt(single_cost), _fmt(double_cost),
            _fmt(single_cost), _fmt(double_cost),
            _fmt(single_cost), _fmt(double_cost),
            _fmt(single_cost), _fmt(double_cost),
            row_num,
        ])
        count += 1

    # Tiered items
    for tier_def in _TIER_DEFS:
        tier_name = tier_def["name"]
        for row_num in range(tier_def["data_start"], tier_def["data_end"] + 1):
            item_name = _clean_str(_cell(ws, row_num, 1))
            if not item_name:
                continue

            c_s_lt190 = _to_decimal(_cell(ws, row_num, 12)) or _to_decimal(_cell(ws, row_num, 10))
            c_d_lt190 = _to_decimal(_cell(ws, row_num, 13)) or _to_decimal(_cell(ws, row_num, 11))
            c_s_191 = _to_decimal(_cell(ws, row_num, 14)) or c_s_lt190
            c_d_191 = _to_decimal(_cell(ws, row_num, 15)) or c_d_lt190
            c_s_250 = _to_decimal(_cell(ws, row_num, 16)) or c_s_lt190
            c_d_250 = _to_decimal(_cell(ws, row_num, 17)) or c_d_lt190
            c_s_300 = _to_decimal(_cell(ws, row_num, 18)) or c_s_lt190
            c_d_300 = _to_decimal(_cell(ws, row_num, 19)) or c_d_lt190

            writer.writerow([
                tier_name,
                item_name,
                "tiered",
                "",  # condition_description
                _fmt(c_s_lt190), _fmt(c_d_lt190),
                _fmt(c_s_191), _fmt(c_d_191),
                _fmt(c_s_250), _fmt(c_d_250),
                _fmt(c_s_300), _fmt(c_d_300),
                row_num,
            ])
            count += 1

    fh.close()
    return count


def extract_guideline_types(ws, out_dir: str) -> int:
    """Extract guideline_types.csv"""
    path = os.path.join(out_dir, "guideline_types.csv")
    fh, writer = _open_csv(path, [
        "short_name", "description", "sort_order",
        "category_code", "category_name", "notes", "default_price",
    ])
    count = 0
    for col_idx, short_name in sorted(_GUIDELINE_SHORT_NAMES.items()):
        full_desc = _clean_str(_cell(ws, 10, col_idx)) or short_name
        category_name = _GUIDELINE_CATEGORY_NAMES.get(short_name, "")
        writer.writerow([
            short_name, full_desc, col_idx - 9,
            short_name, category_name, "", "0",
        ])
        count += 1
    fh.close()
    return count


def extract_estate_guidelines(ws, out_dir: str) -> int:
    """Extract estate_guidelines.csv"""
    path = os.path.join(out_dir, "estate_guidelines.csv")
    fh, writer = _open_csv(path, [
        "estate_name", "stage_name", "guideline_type", "cost", "override_text",
    ])
    count = 0
    row = 11
    while True:
        estate_name = _clean_str(_cell(ws, row, 1))
        if estate_name is None:
            if all(_clean_str(_cell(ws, row + i, 1)) is None for i in range(5)):
                break
            row += 1
            continue

        stage_val = _clean_str(str(_cell(ws, row, 2)) if _cell(ws, row, 2) is not None else "")

        for col_idx, short_name in _GUIDELINE_SHORT_NAMES.items():
            cell_val = _cell(ws, row, col_idx)
            if cell_val is None:
                continue

            cost = _to_decimal(cell_val)
            override_text = None
            if cost is None:
                override_text = _clean_str(cell_val)
                if override_text is None:
                    continue

            writer.writerow([
                estate_name,
                _fmt(stage_val),
                short_name,
                _fmt(cost),
                _fmt(override_text),
            ])
            count += 1

        row += 1

    fh.close()
    return count


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Extract pricing workbook to CSV files")
    parser.add_argument(
        "--workbook",
        default="Reference/Pricing sheet 2026.xlsm",
        help="Path to the Excel workbook",
    )
    parser.add_argument(
        "--brand",
        default="Hermitage Homes",
        help="Brand name (default: Hermitage Homes)",
    )
    parser.add_argument(
        "--output",
        default="data/seed",
        help="Output directory for CSV files (default: data/seed)",
    )
    args = parser.parse_args()

    out_dir = args.output
    os.makedirs(out_dir, exist_ok=True)

    print(f"Loading workbook: {args.workbook}")
    wb = openpyxl.load_workbook(args.workbook, data_only=True, read_only=False)

    try:
        # --- Houses sheet ---
        ws_houses = wb["Houses"]

        n = extract_house_designs(ws_houses, args.brand, out_dir)
        print(f"  house_designs.csv: {n} records")

        n = extract_house_facades(ws_houses, args.brand, out_dir)
        print(f"  house_facades.csv: {n} records")

        n = extract_energy_ratings(ws_houses, args.brand, out_dir)
        print(f"  energy_ratings.csv: {n} records")

        n = extract_fbc_bands(ws_houses, args.brand, out_dir)
        print(f"  fbc_escalation_bands.csv: {n} records")

        # --- Upgrades sheet ---
        ws_upgrades = wb["Upgrades"]
        cat_n, item_n = extract_upgrades(ws_upgrades, args.brand, out_dir)
        print(f"  upgrade_categories.csv: {cat_n} records")
        print(f"  upgrade_items.csv: {item_n} records")

        # --- GROUPS sheet ---
        ws_groups = wb["GROUPS"]
        grp_n, comm_n = extract_wholesale_groups_and_commissions(
            ws_groups, args.brand, out_dir,
        )
        print(f"  wholesale_groups.csv: {grp_n} records")
        print(f"  commission_rates.csv: {comm_n} records")

        # --- ESTATES sheet ---
        ws_estates = wb["ESTATES"]

        n = extract_travel_surcharges(ws_estates, out_dir)
        print(f"  travel_surcharges.csv: {n} records")

        n = extract_guideline_types(ws_estates, out_dir)
        print(f"  guideline_types.csv: {n} records")

        n = extract_estate_guidelines(ws_estates, out_dir)
        print(f"  estate_guidelines.csv: {n} records")

        # --- Site Costs sheet ---
        ws_site_costs = wb["Site Costs"]

        n = extract_postcode_site_costs(ws_site_costs, out_dir)
        print(f"  postcode_site_costs.csv: {n} records")

        n = extract_site_cost_tiers(out_dir)
        print(f"  site_cost_tiers.csv: {n} records")

        n = extract_site_cost_items(ws_site_costs, out_dir)
        print(f"  site_cost_items.csv: {n} records")

    finally:
        wb.close()

    print(f"\nDone. CSV files written to {out_dir}/")


if __name__ == "__main__":
    main()

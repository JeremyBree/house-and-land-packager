# Data Extraction Mapping — Pricing Workbook to CSV

This document maps every data field from the Pricing sheet 2026.xlsm workbook to the corresponding CSV output file and database column.

## Source Workbook Sheets

| Sheet Name | Entities Extracted |
|---|---|
| Houses | HouseDesign, HouseFacade, EnergyRating, FbcEscalationBand |
| Upgrades | UpgradeCategory, UpgradeItem |
| ESTATES | GuidelineType, EstateDesignGuideline, TravelSurcharge |
| Site Costs | PostcodeSiteCost, SiteCostTier, SiteCostItem |
| GROUPS | WholesaleGroup, CommissionRate |

---

## 1. house_designs.csv

**Source:** Houses sheet, rows 4+, cols A-J (1-10)
**Stop condition:** 3 consecutive blank rows in col A

| CSV Column | Excel Column | Cell Index | Type | Notes |
|---|---|---|---|---|
| brand | (parameter) | — | string | Passed as script argument, default "Hermitage Homes" |
| house_name | A | 1 | string | Required. Used as FK reference by facades/energy ratings |
| base_price | B | 2 | decimal | Strip $ and commas |
| storey | C | 3 | string | Default "Single" if blank |
| frontage | D | 4 | decimal | |
| depth | E | 5 | decimal | |
| gf_sqm | F | 6 | decimal | |
| total_sqm | G | 7 | decimal | |
| lot_total_sqm | H | 8 | decimal | |
| squares | I | 9 | integer | |
| details | J | 10 | string | Nullable |

**DB unique key:** (brand, house_name)

---

## 2. house_facades.csv

**Source:** Houses sheet, rows 4+, cols A (house context) + K-M (11-13)
**Note:** Multiple facades per house. A new house_name in col A sets the current design context.

| CSV Column | Excel Column | Cell Index | Type | Notes |
|---|---|---|---|---|
| brand | (parameter) | — | string | |
| house_name | A | 1 | string | FK reference to house_designs |
| facade_name | K | 11 | string | Required |
| facade_price | L | 12 | decimal | 0 if "Included" |
| facade_details | M | 13 | string | Nullable |
| is_included | L | 12 | boolean | True if cell text is "Included" or price is blank |

**DB unique key:** (design_id resolved from house_name+brand, facade_name)

---

## 3. energy_ratings.csv

**Source:** Houses sheet, rows 4+, cols R-W (18-23)

| CSV Column | Excel Column | Cell Index | Type | Notes |
|---|---|---|---|---|
| brand | (parameter) | — | string | |
| house_name | R | 18 | string | FK reference to house_designs |
| garage_side | S | 19 | string | "LHS" or "RHS" |
| orientation | T | 20 | string | N, NE, E, SE, S, SW, W, NW |
| star_rating | U | 21 | decimal | |
| best_worst | V | 22 | string | "B" or "W" |
| compliance_cost | W | 23 | decimal | |

**DB unique key:** (design_id resolved from house_name+brand, garage_side, orientation)

---

## 4. fbc_escalation_bands.csv

**Source:** Houses sheet, rows 4+, cols AT-AV (46-48)

| CSV Column | Excel Column | Cell Index | Type | Notes |
|---|---|---|---|---|
| brand | (parameter) | — | string | |
| day_start | AT | 46 | integer | |
| day_end | AU | 47 | integer | |
| multiplier | AV | 48 | decimal | |

**DB unique key:** (brand, day_start)

---

## 5. upgrade_categories.csv

**Source:** Upgrades sheet, rows 2+, col B
**Detection:** Rows matching pattern `***CATEGORY_NAME***`

| CSV Column | Excel Column | Cell Index | Type | Notes |
|---|---|---|---|---|
| brand | (parameter) | — | string | |
| name | B | 2 | string | Extracted from `***name***` pattern |
| sort_order | (computed) | — | integer | Sequential per category |

**DB unique key:** (brand, name) — checked by query

---

## 6. upgrade_items.csv

**Source:** Upgrades sheet, rows 2+, cols A-D (non-category rows)

| CSV Column | Excel Column | Cell Index | Type | Notes |
|---|---|---|---|---|
| brand | (parameter) | — | string | |
| category_name | (context) | — | string | FK reference — current category from last `***NAME***` marker |
| description | B | 2 | string | Required |
| price | C | 3 | decimal | |
| date_added | A | 1 | date | YYYY-MM-DD format, nullable |
| notes | D | 4 | string | Nullable |
| sort_order | (computed) | — | integer | Sequential within category |

**DB unique key:** (brand, description) — checked by query

---

## 7. wholesale_groups.csv

**Source:** GROUPS sheet, rows 3+, multiple BDM column blocks
**BDM column blocks:** (3,4,5,6), (8,9,10,11), (13,14,15,16), (18,19,20,21), (23,24,25,26), (28,29,30,31), (33,34,35,36), (38,39,40,41), (43,44,45,46)
**Extracted from:** name_col (first column in each block)

| CSV Column | Source | Type | Notes |
|---|---|---|---|
| group_name | name_col value | string | Deduplicated across all BDM blocks |
| gst_registered | gst_col value | boolean | yes/y/true/1 = True |
| active | (default) | boolean | Always True |

**DB unique key:** (group_name)

---

## 8. commission_rates.csv

**Source:** GROUPS sheet, rows 3+, multiple BDM column blocks
**BDM name:** Row 2 of each block's name_col

| CSV Column | Source | Type | Notes |
|---|---|---|---|
| brand | (parameter) | string | |
| bdm_email | (cross-ref) | string | Looked up from BDM first_name in profiles table |
| group_name | name_col value | string | FK reference to wholesale_groups |
| commission_fixed | comms_col value | decimal | Nullable |
| commission_pct | pct_col value | decimal | Nullable |

**DB unique key:** (bdm_profile_id resolved from bdm_email, group_id resolved from group_name)

---

## 9. travel_surcharges.csv

**Source:** ESTATES sheet, rows 11+, cols AO-AQ (41-43)

| CSV Column | Excel Column | Cell Index | Type | Notes |
|---|---|---|---|---|
| suburb_name | AO | 41 | string | Full text including postcode |
| postcode | AO | 41 | string | Last 4 digits if numeric, extracted from suburb_name |
| surcharge_amount | AP | 42 | decimal | |
| region_name | AQ | 43 | string | Nullable |

**DB unique key:** (suburb_name)

---

## 10. postcode_site_costs.csv

**Source:** Site Costs sheet, rows 22-78, cols J-K (10-11)

| CSV Column | Excel Column | Cell Index | Type | Notes |
|---|---|---|---|---|
| postcode | J | 10 | string | Converted from int via str(int(...)) |
| rock_removal_cost | K | 11 | decimal | |

**DB unique key:** (postcode) — primary key

---

## 11. site_cost_tiers.csv

**Source:** Site Costs sheet — 3 fixed tier definitions

| CSV Column | Source | Type |
|---|---|---|
| tier_name | Hardcoded | string |
| fall_min_mm | Hardcoded | integer |
| fall_max_mm | Hardcoded | integer |

**Fixed data:**
| tier_name | fall_min_mm | fall_max_mm |
|---|---|---|
| 0-1000mm | 0 | 1000 |
| 1001-1500mm | 1001 | 1500 |
| 1501-2000mm | 1501 | 2000 |

**DB unique key:** (tier_name) — checked by query

---

## 12. site_cost_items.csv

**Source:** Site Costs sheet
- Basic items: rows 18-20, 80-83, cols D-F (4-6)
- Tiered items: rows per tier (87-94, 99-107, 112-121), cols A + J-S (1, 10-19)

| CSV Column | Excel Column | Type | Notes |
|---|---|---|---|
| tier_name | (context) | string | Nullable for basic items, tier name for tiered |
| item_name | A or hardcoded | string | |
| condition_type | (computed) | string | "basic" or "tiered" |
| condition_description | F (basic only) | string | Nullable |
| cost_single_lt190 | L or D (14 or 4) | decimal | Fallback to J (10) if null |
| cost_double_lt190 | M or E (15 or 5) | decimal | Fallback to K (11) if null |
| cost_single_191_249 | N (14) | decimal | |
| cost_double_191_249 | O (15) | decimal | |
| cost_single_250_300 | P (16) | decimal | |
| cost_double_250_300 | Q (17) | decimal | |
| cost_single_300plus | R (18) | decimal | |
| cost_double_300plus | S (19) | decimal | |
| sort_order | (row number) | integer | |

**DB unique key:** (tier_id resolved from tier_name, item_name)

---

## 13. guideline_types.csv

**Source:** ESTATES sheet, row 10 (header row), cols J-AJ (10-36)

| CSV Column | Source | Type | Notes |
|---|---|---|---|
| short_name | Column-to-name mapping | string | See mapping table below |
| description | Header cell text at row 10 | string | Full description from worksheet |
| sort_order | (col_index - 9) | integer | |

**Short name mapping (col index → short_name):**

| Col | Short Name |
|---|---|
| 10 | recycled_water |
| 11 | fibre_optic |
| 12 | eaves_1500 |
| 13 | eaves_3000 |
| 14 | water_tank_2000_garden |
| 15 | water_tank_2000_toilets |
| 16 | water_tank_5000_toilets |
| 17 | timber_fencing_additional |
| 18 | timber_fencing_capping |
| 19 | colourbond_fencing |
| 20 | timber_fencing_exposed_125x125 |
| 21 | timber_fencing_exposed_125x75 |
| 22 | roof_pitch_25deg |
| 23 | colorbond_roofing |
| 24 | flat_roof_tiles_cat3 |
| 25 | colour_through_concrete |
| 26 | corner_treatment |
| 27 | brickwork_above_garage |
| 28 | brickwork_above_windows |
| 29 | exposed_aggregate_concrete |
| 30 | ceiling_2590mm |
| 31 | ceiling_2720mm |
| 32 | rendered_front_projection |
| 33 | rendered_whole_facade |
| 34 | travel_surcharge |
| 35 | advanced_trees_landscaping |
| 36 | single_crossover_footpath |

**DB unique key:** (short_name)

---

## 14. estate_guidelines.csv

**Source:** ESTATES sheet, rows 11+, cols A-B (estate/stage identity) + J-AJ (guideline values)

| CSV Column | Source | Type | Notes |
|---|---|---|---|
| estate_name | Col A (1) | string | FK reference to estates table |
| stage_name | Col B (2) | string | FK reference to estate_stages table, nullable |
| guideline_type | (column short_name) | string | FK reference to guideline_types.short_name |
| cost | Cell value | decimal | If cell is numeric |
| override_text | Cell value | string | If cell is text (non-numeric) |

**Note:** Each estate row produces up to 27 CSV rows (one per guideline column that has a value).

**DB unique key:** (estate_id resolved from estate_name, stage_id resolved from stage_name, type_id resolved from guideline_type)

---

## Import Order (FK Dependencies)

```
Tier 1 (independent):
  house_designs, upgrade_categories, wholesale_groups,
  travel_surcharges, postcode_site_costs, fbc_escalation_bands,
  site_cost_tiers, guideline_types

Tier 2 (depends on Tier 1):
  house_facades → house_designs
  energy_ratings → house_designs
  upgrade_items → upgrade_categories
  commission_rates → wholesale_groups + profiles
  site_cost_items → site_cost_tiers
  estate_guidelines → estates + estate_stages + guideline_types
```

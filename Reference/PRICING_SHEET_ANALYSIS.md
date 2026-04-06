# Excel Pricing Template Analysis

**Source:** `C:\Projects\HouseAndLand\Reference\Pricing sheet .xlsm`
**Pricing effective date:** 1st June 2025
**Analysis date:** 2026-04-05

---

## 1. Entity Catalog

### 1.1 Houses (Table1) -- `Houses!A3:P359`

The master catalog of house designs and their facade variants. Each row is a **(house, facade)** combination -- not a unique house.

| Column | Header | Type | Input/Calc | Notes |
|--------|--------|------|-----------|-------|
| A (1) | House | VARCHAR(100) | Input | House design name (e.g., "Access 18 HPS") |
| B (2) | Price | NUMERIC(10,2) | Input | Base house price excl. facade |
| C (3) | Storey | VARCHAR(10) | Input | "Single" or "Double" |
| D (4) | Frontage | NUMERIC(6,2) | Input | Minimum lot frontage required (metres) |
| E (5) | Depth | NUMERIC(6,2) | Input | Minimum lot depth required (metres) |
| F (6) | GF m2 | NUMERIC(8,2) | Input | Ground floor area |
| G (7) | Total m2 | NUMERIC(8,2) | Input | Total floor area (both storeys) |
| H (8) | Lot Total | NUMERIC(10,2) | **Calc** | `= Frontage * Depth` (minimum lot m2) |
| I (9) | Squares | INTEGER | Input | House size in squares |
| J (10) | House Details | TEXT | Input | e.g., "3 Bed, 3 Bath, Single Car Garage, 1 Living, ODL" |
| K (11) | Facade | VARCHAR(100) | Input | Facade name (e.g., "Holt", "Duke", "Sorrento") |
| L (12) | Facade Price | VARCHAR/NUM | Input | "Included" or dollar amount (1500-19900) |
| M (13) | Facade Details | TEXT | Input | Description of facade features |
| N (14) | Design source/reason | TEXT | Input | Internal notes |
| O (15) | Facade source/reason | TEXT | Input | Internal notes |
| P (16) | Column1 | - | - | Empty/unused |

**Data volumes:**
- 356 rows (house-facade combos)
- **57 unique house designs**
- Facades per house: min 1, max 7, avg 6.2
- Storey types: Single, Double
- Facade prices: Included, $1,500, $3,000, $3,900, $4,000, $4,900, $19,900

**Primary key:** Composite (House + Facade)
**Business rule:** A single house design repeats once per facade option. All columns except Facade, Facade Price, and Facade Details are duplicated across rows for the same house.

### 1.2 Energy Ratings (Table12) -- `Houses!R3:W1123`

Star ratings and energy compliance costs for every (house, garage side, orientation) combination.

| Column | Header | Type | Notes |
|--------|--------|------|-------|
| R (18) | House | VARCHAR(100) | FK to Table1[House] |
| S (19) | Garage Side | VARCHAR(10) | "Left" or "Right" |
| T (20) | Orientation | VARCHAR(5) | N, NE, E, SE, S, SW, W, NW |
| U (21) | Updated Star Rating | NUMERIC(3,1) | 6.8 to 8.1 |
| V (22) | Best / Worst | VARCHAR(1) | "B" or "W" |
| W (23) | Cost | INTEGER | 5000, 8000, or 15000 |

**Data volumes:**
- 1,120 rows
- 70 unique houses
- Exactly 16 orientation records per house (2 garage sides x 8 compass directions)

**Primary key:** Composite (House + Garage Side + Orientation)
**Business rule:** Cost is $5,000 for "Best" orientations, $8,000 or $15,000 for "Worst". This feeds into the pricing engine as energy compliance cost.

### 1.3 FBC Escalation (Table3) -- `Houses!AT3:AV39`

Future Build Cost escalation table -- percentage markup based on days between pricing date and contract date.

| Column | Header | Type |
|--------|--------|------|
| AT (46) | FBC Day 1 | INTEGER (start of range) |
| AU (47) | FBC Day 2 | INTEGER (end of range) |
| AV (48) | % | NUMERIC(5,3) (multiplier, e.g., 1.003) |

**Sample:** 30-59 days = 1.003 (0.3%), 60-89 days = 1.006, etc. Escalation increases 0.3% per 30-day period.

### 1.4 Sales Estimator List (Table2) -- `Houses!Z3:Z11`

Simple dropdown list of sales estimator names (8 people).

### 1.5 Upgrades (Table4) -- `Upgrades!A1:D191`

The master upgrade catalog for Hermitage Homes brand.

| Column | Header | Type | Notes |
|--------|--------|------|-------|
| A (1) | Date added | DATE | When upgrade was created |
| B (2) | Hermitage Homes - Upgrades | TEXT | Full specification text |
| C (3) | $$ | NUMERIC(10,2) | Price (can be negative for downgrades) |
| D (4) | Notes | TEXT | Additional context |

**Data volumes:**
- 190 upgrade items (including category separators)
- Categories (delimited by `***NAME***` rows):
  - PACKS (combo deals, $-5000 to $14,999)
  - CEILING HEIGHTS
  - EXTERNALS (brickwork, eaves, tanks, fencing, roofing, concrete, landscaping)
  - INTERNALS (doors, stairs, cabinetry, finishes)
  - ELECTRICAL (lights, GPOs, fans, solar, security)
  - HEATING & COOLING (split systems, evap, RCAC)
  - KITCHEN (benchtops, sinks, appliances, splashbacks)
  - LAUNDRY
  - BATHROOM/ENSUITE/POWDER (tiles, basins, showers, toilets)
  - FLOOR COVERINGS (carpet, tiles, hybrid)
  - GROUP/HOUSE RELATED (group-specific inclusions, markups)
  - REGULATORY (performance solutions, permits)

**Primary key:** Upgrade description text (col B) -- used as lookup key
**Business rule:** Upgrades are looked up by exact description text via XLOOKUP. The `$$` column feeds into `$Y$24:$Y$50` in the Pricing Sheet.

### 1.6 KBC Upgrades (Table417) -- `Upgrades!J1:M3`

Kingsbridge Complete upgrades -- same structure, only 2 items.

### 1.7 Townhomes Upgrades (Table22) -- `Upgrades!P1:S30`

Townhomes brand upgrades -- 29 items, has `$$Retail` instead of `$$`.

### 1.8 ESTATES (Table6) -- `ESTATES!A10:AJ4795`

The estate/lot database AND the design guideline configuration matrix. This is the largest and most complex sheet.

**Columns 1-9: Estate identity**

| Column | Header | Type | Notes |
|--------|--------|------|-------|
| A (1) | Estate | VARCHAR(255) | Estate name |
| B (2) | Stage | VARCHAR(50) | Stage number or "No Stage" |
| C (3) | Suburb | VARCHAR(100) | Suburb + postcode (e.g., "Clyde North 3978") |
| D (4) | Concatenate | CALC | `=CONCATENATE(A,B)` -- composite key for lookups |
| E (5) | POS number | VARCHAR(20) | Plan of Subdivision number |
| F (6) | Developer | VARCHAR(255) | Developer/owner name |
| G (7) | Contact | VARCHAR(255) | Contact name or agency |
| H (8) | Contact mobile | VARCHAR(50) | Phone number |
| I (9) | Contact email | VARCHAR(255) | Email address |

**Columns 10-36: Design guideline requirements (the "cost matrix")**

Each column is a specific design guideline item. The **header text IS the upgrade specification** (full description of what's required). The **cell value** is either:
- A numeric cost amount
- A formula referencing a shared cost row (e.g., `=J$7`, `=Q$2`, `=Z$7`)
- A text description (overriding the column header)
- Empty (guideline not required for this estate)

| Col | Guideline Item | Typical Values |
|-----|---------------|----------------|
| J (10) | 3rd pipe recycled water | Cost from J$7 row (varies by provider) |
| K (11) | Fibre optic | Text description of NBN/Opticomm/etc. requirements |
| L (12) | 450mm eaves, 1500mm return | Cost or formula |
| M (13) | 450mm eaves, 3000mm return | Cost or formula |
| N (14) | 2000L water tank (garden tap) | Text or cost |
| O (15) | 2000L water tank (toilets) | Cost or formula |
| P (16) | 5000L water tank (toilets) | Text or cost |
| Q (17) | Additional timber fencing | Cost formula from row 2 |
| R (18) | Timber fencing with capping | Cost formula |
| S (19) | Colourbond fencing | Cost or text |
| T (20) | Timber fencing with exposed posts (125x125) | Cost formula |
| U (21) | Timber fencing with exposed posts (125x75) | Cost formula |
| V (22) | 25-degree roof pitch | Text indicator |
| W (23) | Colorbond roofing | Cost formula |
| X (24) | Category 3 flat roof tiles | Cost formula |
| Y (25) | Colour-through concrete | Text indicator |
| Z (26) | Corner treatment (second frontage) | Cost from Z$7 |
| AA (27) | Brickwork above garage door | Cost formula |
| AB (28) | Brickwork above all windows/doors | Cost formula |
| AC (29) | Exposed aggregate concrete | Text or cost |
| AD (30) | 2590mm ceiling height | Text indicator |
| AE (31) | 2720mm ceiling height | Cost formula |
| AF (32) | Rendered front projection | Cost formula |
| AG (33) | Rendered whole facade | Text indicator |
| AH (34) | Travel surcharge | Formula: XLOOKUP by suburb in Table5 |
| AI (35) | Advanced trees & landscaping | Cost formula |
| AJ (36) | Single crossover & footpath | Cost or formula |

**Columns 38-39: UI helper columns**
- Col 38 (AL): "Single List" -- array formula generating unique estate list for dropdowns
- Col 39 (AM): "Stage List" -- array formula for stage dropdowns

**Data volumes:**
- 4,785 estate-stage rows
- **861 unique estates**
- **241 unique suburbs**
- **236 unique developers**

**Primary key:** Concatenate (Estate + Stage) -- column D
**Foreign keys:** Suburb links to Table5 (Travel Surcharge)

### 1.9 Travel Surcharge (Table5) -- `ESTATES!AO10:AQ165`

Suburb-to-surcharge lookup table.

| Column | Header | Type |
|--------|--------|------|
| AO (41) | Travel Surcharge | VARCHAR(100) (suburb name) |
| AP (42) | $$ | NUMERIC(10,2) |
| AQ (43) | Region | VARCHAR(50) |

**Sample:** Ballarat suburbs = $8,000; Armstrong Creek = $1,500.
**Business rule:** Travel surcharge is determined by suburb. All Ballarat-region suburbs share the same $8,000 surcharge.

### 1.10 GROUPS (BDM Commission Tables)

The GROUPS sheet contains **one table per BDM (Business Development Manager)**, each mapping wholesale groups to commission amounts.

**Table10 (A2:A11):** List of 9 BDM names (Bec, Layal, Simone, Caitlin, Josh, Peter, William, Vattey, Matthew).

**Per-BDM tables (e.g., Bec at C2:F54):**

| Column | Header | Type |
|--------|--------|------|
| 1 | [BDM Name] | VARCHAR(100) -- wholesale group name |
| 2 | comms inc GST | NUMERIC(10,2) -- fixed commission amount |
| 3 | comms % | NUMERIC(5,3) -- percentage-based commission |
| 4 | regstd for GST | VARCHAR(5) -- GST registration flag |

**Business rule:** Each BDM manages different wholesale groups with different commission amounts. The Pricing Sheet uses `VLOOKUP(B11,INDIRECT(A11),2,FALSE)` where:
- A11 = BDM name (selects which table to look up)
- B11 = Wholesale group name (row lookup within that BDM's table)
- Returns commission amount from column 2

**Data volumes:**
- Bec: 52 groups, Layal: 52, Simone: 25, Caitlin: 22, Josh: 12, Peter: 55, William: 32, Vattey: 220, Matthew: 10
- Commission ranges: $33,000 to $63,800 fixed, or 6.6% percentage-based

### 1.11 Site Costs

A complex cost calculator organized in three fall-range tiers.

**Input parameters (rows 1-13):**
- Lot address, house type, range (Inspire/Elegance)
- Existing neighbours flag, rear easement depth, lot size, postcode
- Fall over lot (calculated from corner levels in mm)

**Basic site costs (rows 17-83):**
- Row 18: H2 waffle foundation ($30/m2 of ground floor)
- Row 19: Minimum piering ($1,659)
- Rows 22-78: **Postcode-specific rock removal costs** -- 57 postcodes mapped to costs ($0 to $9,750)
- Row 80: Front retaining walls ($5,400 single / $9,000 double)
- Row 81: Second soil test & survey ($1,915)
- Row 82: Manual handling for restricted sites ($2,535)
- Row 83: Services & connections under 650m2 ($1,700)

**Fall-range tiers (each has the same structure):**

| Tier | Rows | Fall Range |
|------|------|-----------|
| 0-1000mm | 84-95 | Standard fall |
| 1001-1500mm | 96-108 | Moderate fall |
| 1501-2000mm | 109-122 | Steep fall |

**Per-tier items (8 size bands: Single/Double x <190/191-249/250-300/300+ m2):**

| Line Item | Condition | Cost Pattern |
|-----------|-----------|-------------|
| Excavation | Fall > 0.3m (60% rule) | Size-banded ($1,761-$3,500) |
| Fully piered home | Fill/Trees flag | Size-banded ($1,814-$8,500) |
| Easement proximity | Within 2m of easement | Fixed ($3,000-$4,000) |
| LHS Retaining | Retaining wall needed left | Size-banded ($2,750-$12,000) |
| RHS Retaining | Retaining wall needed right | Size-banded ($2,750-$12,000) |
| Lot over 650m2 | Rear setback > 6m | Variable ($97/m beyond 6m) |
| 460mm slab | Fill/Trees flag | Variable ($12/m2) |
| Unbalanced cut/fill (GWH) | Elegance range, setback < 0.21m | Size-banded |
| Driveway gradient (Tier 3 only) | Fall > 1.79m, setback < 6.1m | Size-banded |

**Total formula:** `=IF(AND(B7="Single",B13>0,B13<=1000),SUM(D17:D83,D87:D94),"")`

### 1.12 Tender Sheets (Output Documents)

Five tender template sheets (Single Tender, 1B - Tender, HPS - Tender, IL - Tender, Double Tender) are **document templates**, not data tables. They pull values from the Pricing Sheet via formulas:

- Rows 171-197: `=_xlfn.CONCAT('Pricing Sheet'!A24:L24)` -- estate guideline descriptions
- Rows 212-224: `=_xlfn.CONCAT('Pricing Sheet'!O24:X24)` -- upgrade descriptions
- House/facade lookups: `XLOOKUP(B22,Table1[House],Table1[House Details])`

### 1.13 KBC Houses (Table118) -- `KBC - Houses!A3:O47`

Kingsbridge Complete brand house catalog. Same structure as Table1 but:
- 44 rows (fewer house designs)
- Price column = different price list (lower prices, e.g., $272,300 vs $390,000)
- Pricing date: August 2025

### 1.14 KTH Tender (Table124) -- `KTH - Tender!I2:M10`

Kingsbridge Townhomes address lookup table with 8 townhome addresses.

---

## 2. Relationship Diagram

```
                    +----------------+
                    |    Regions     |
                    |  (Table5)     |
                    +-------+--------+
                            |
                            | suburb -> region
                            v
+------------+     +--------+--------+     +------------------+
| Developers | <-- |    ESTATES      | --> | Travel Surcharge |
|            |     |   (Table6)      |     |   (Table5)       |
+------------+     | estate+stage PK |     +------------------+
                    +--------+--------+
                             |
           estate+stage      |  XLOOKUP by Concatenate (estate+stage)
           guidelines        |
           (cols 10-36)      v
                    +--------+--------+
                    |  Pricing Sheet  |   <-- BDM/Group selection
                    |  (rows 11-20)   |
                    +--+--+--+--+----+
                       |  |  |  |
        XLOOKUP        |  |  |  |     VLOOKUP(INDIRECT)
        by house       |  |  |  |
                       v  |  |  v
              +---------+ |  | +----------+
              | Houses   | |  | | GROUPS   |
              | (Table1) | |  | | (per-BDM)|
              +----+-----+ |  | +----------+
                   |        |  |
                   |        |  |  XLOOKUP by upgrade name
                   |        |  v
              +----+-----+  | +-----------+
              | Energy   |  | | Upgrades  |
              | Ratings  |  | | (Table4)  |
              | (Table12)|  | +-----------+
              +----------+  |
                            v
                    +-------+--------+
                    |  Site Costs    |
                    | (postcode +    |
                    |  fall-based)   |
                    +----------------+
```

### Foreign Key Map

| From | To | Join Condition |
|------|----|---------------|
| Pricing Sheet.C3 (Estate) | Table6[Estate] | XLOOKUP by estate name |
| Pricing Sheet.K11 (House Type) | Table1[House] | XLOOKUP by house name |
| Pricing Sheet.M11 (Facade) | Table1[Facade] | INDEX/MATCH by (House + Facade) |
| Pricing Sheet.A11 (BDM) | GROUPS table name | INDIRECT() -- dynamic table reference |
| Pricing Sheet.B11 (Wholesale Group) | GROUPS[BDM_name] | VLOOKUP by group name |
| Table6[Suburb] | Table5[Travel Surcharge] | XLOOKUP by suburb name |
| Table6[Concatenate] | Table6[cols 10-36] | Self-reference by estate+stage |
| Table12[House] | Table1[House] | Same house name |
| Pricing Sheet rows 24-50 | Upgrades[Hermitage Homes - Upgrades] | XLOOKUP by description text |

---

## 3. Business Rules Extracted

### 3.1 House Price Lookup (Col 15 / O)

```
IF estate is NOT "Bankside Estate":
    House Price = XLOOKUP(house_type, Table1[House], Table1[Price])
ELSE IF estate IS "Bankside Estate":
    Only allow facades: Bankside, Forde, Elite, Menzies, Keating
    Otherwise show error "BANKSIDE,FORDE,ELITE,MENZIES,KEATING ONLY"
```

**Business rule:** Bankside Estate has facade restrictions. All other estates can use any facade.

### 3.2 Facade Price Lookup (Col 16 / P)

```
Facade Price = INDEX(Table1[Facade Price],
    MATCH(1, (Table1[House]=house_type) * (Table1[Facade]=facade_type), 0))
```

**Business rule:** Array formula does a compound lookup matching BOTH house AND facade to find the correct facade price. Returns "Included" or a dollar amount.

### 3.3 Design Guidelines / Estate Requirements (Col 18 / R)

```
IF this lot is NOT a corner block AND no other lots in the batch are corner blocks:
    Design Guidelines = SUM(M$24:M$50) - $4,620
    (subtract corner treatment cost since not needed)
ELSE:
    Design Guidelines = SUM(M$24:M$50)
    (full estate requirements including corner treatment)
```

**Business rule:** Corner blocks incur an additional ~$4,620 for corner treatment. The design guidelines cost is the sum of all estate-specific requirements (rows 24-50, col M) which are populated via XLOOKUP from Table6 columns 10-36.

### 3.4 Extra Landscaping (Col 19 / S)

```
Extra Landscaping = (Lot Size - House Lot Total) * $39/sqm
IF lot size <= house minimum lot total: no charge
```

**Business rule:** Any lot area beyond what the house minimally requires costs $39/m2 for additional landscaping.

### 3.5 Upgrades (Col 20 / T)

```
Base = SUM($Y$24:$Y$50)  -- sum of all auto-selected upgrades
MINUS: If house is NOT an "HPS" type, subtract $Y$44 (HPS-specific upgrade)
MINUS: If facade is Holt/Traditional/Prominent/Elite/Sorrento, no facade upgrade deduction
       Otherwise, subtract $Y$24 (neutralizing upgrade -- only for listed facades)
PLUS:  If KDRB flag = "Yes", add $25,000
```

**Business rule:**
1. Upgrades are auto-populated in rows 24-50 based on estate, suburb, wholesale group, and house type
2. HPS-suffix houses get an HPS-specific upgrade; non-HPS houses have it removed
3. Certain "standard" facades (Holt, Traditional, Prominent, Elite, Sorrento) include neutralizing; others don't
4. KDRB (Knock Down Rebuild) adds a flat $25,000 surcharge

### 3.6 Discounts / Price Increase (Col 21 / U)

```
IF lot size < 300m2 OR suburb is in Latrobe Valley region:
    Discount = $5,000
ELSE IF wholesale group = "Dwellings Property Group":
    Discount = $3,000
ELSE:
    No discount
```

**Latrobe Valley suburbs:** Moe 3825, Morwell 3840, Traralgon 3844, Churchill 3842, Boolarra 3870, Glengarry 3854, Newborough 3825, Traralgon South 3844, Toongabbie 3856, Tyers 3844, Yallourn North 3825, Yinnar 3869

### 3.7 Total Build Price (Col 23 / W)

```
Component sum = House Price + Facade Price + Site Costs + Design Guidelines
                + Extra Landscaping + Upgrades + Discounts + Comms Adjustment

IF commission is a fixed amount (not blank):
    Build Price = ROUNDUP(
        (Component sum - Design Guidelines)
        - (33000 - Commission + Comms Adjustment)
        + FBC adjustment
    , -2) + Design Guidelines

IF commission via percentage:
    Build Price = ROUNDUP(
        (Component sum - Design Guidelines)
        - 33000 + FBC adjustment + Commission
    , -2) + Design Guidelines

IF FBC adjustment exists (contract date > 30 days from pricing date):
    Add FBC to build price via Z11 formula
```

**Business rule:** Build price rounds UP to nearest $100 (-2 means two decimal places from the left). The $33,000 is the **base commission** that gets netted out. Design Guidelines are excluded from the rounding to keep them exact.

### 3.8 Total Package Price (Col 24 / X)

```
IF commission is fixed amount:
    Package Price = Land Price + Build Price

IF commission is percentage-based:
    Package Price = ROUNDUP(
        (Land Price + Build Price) / 0.934
    , -2)
```

**Business rule:** The `/0.934` divisor means a percentage-based commission is 6.6% of package price (1 - 0.934 = 0.066). This inflates the package price to cover the commission margin.

### 3.9 Commission Calculation (Col 25 / Y)

```
Commission = VLOOKUP(wholesale_group, INDIRECT(bdm_name), 2, FALSE)
           + Comms Adjustment
```

**Business rule:** Dynamic table lookup -- the BDM's name in col A selects which commission table to use (via INDIRECT). The wholesale group name in col B selects the row. Returns fixed dollar amount (typically $33,000-$63,800) or calculates from percentage.

### 3.10 House Fits Check (Col 32 / AF)

```
IF lot frontage < house minimum frontage OR lot depth < house minimum depth:
    "No"
ELSE:
    "Yes"
```

### 3.11 Fence Extra Meterage (Col 34 / AH)

```
Extra fence = (lot_frontage - house_frontage) + 2 * (lot_depth - house_depth)
```

**Business rule:** Calculates additional fencing needed beyond the house footprint -- both side returns plus depth difference.

### 3.12 FBC (Future Build Cost) Escalation

```
IF contract date is > 30 days after pricing date:
    FBC % = INDEX(Table3[%], MATCH(days_diff, Table3[FBC Day 1], 1)) - 1
    FBC $ = (House+Facade+Landscaping+Upgrades - Design Guidelines - 33000) * FBC% + 1000

FBC escalation: 0.3% per 30-day period (30-59 days = 0.3%, 60-89 = 0.6%, etc.)
```

### 3.13 10% Holding Costs (Col 26 / Z)

```
IF "10/90 deal" = "Yes" AND "holding costs apply" = "Yes":
    Holding costs = Total Build Price / 10
```

**Business rule:** For 10/90 contracts (10% deposit, 90% on completion), holding costs are 10% of build price.

### 3.14 Estate Guideline Auto-Population (Rows 24-50)

The Pricing Sheet rows 24-50 auto-populate based on the selected estate. Each row:

**Column A:** Looks up the estate+stage in ESTATES sheet column D, then returns the guideline header text from row 10 if the estate has a value in that column.

**Column M:** Looks up the cost for that guideline from the ESTATES sheet using XLOOKUP by Concatenate key.

**Column O:** Auto-selects upgrades based on complex conditional logic:
- Row 24: Neutralizing for certain facades (Holt/Traditional/Prominent/Elite/Sorrento)
- Row 25: Shared crossover re-establishment survey
- Row 26: Stainless steel brick ties for coastal suburbs (Point Cook, Curlewis, etc.)
- Row 27-29: Group-specific upgrade packs (Reventon, Aspire, Axon, Unity Assets, Capital Edge, etc.)
- Row 30: Unity Assets-specific upgrades
- Row 31: Co-living GE house upgrades (Leon 22-1B GE, Leon 25 GE)
- Row 33-34: Atlas/Stack/CR Property group-specific inclusions
- Row 35: Land referral fee
- Row 36: Group-specific inclusions (S.A.P Express, SA Thompson, etc.)
- Row 41-42: Prominent/Alpha facade porch extensions for lots < 300m2
- Row 43-45: House-specific upgrades (Drake 19 GE, Jackson 18, co-living)
- Row 44: HPS fire sprinkler requirements
- Row 49: Preliminary site clean ($2,000 fixed)
- Row 50: Planning permit for Latrobe Valley lots < 500m2 ($5,000)

**Column Y:** Looks up the dollar cost of each auto-selected upgrade from Table4.

---

## 4. Pricing Engine Flow

### Step-by-step pricing calculation:

```
1. BDM SELECTS ESTATE
   -> XLOOKUP populates: suburb, developer, contact details, POS number
   -> Auto-populates estate guideline rows 24-50 (cols A, M, O, Y)

2. BDM ENTERS LOT DETAILS (rows 11-20, up to 10 lots at once)
   Inputs: BDM name, Wholesale Group, Stage, Lot No, Street, Lot Width,
           Lot Depth, Lot Size, Corner Block?, Orientation, House Type,
           Garage Side, Facade Type, Land Price, Site Costs

3. AUTO-CALCULATIONS FIRE:

   a. House Price        = XLOOKUP(house_type -> Table1[Price])
   b. Facade Price       = INDEX/MATCH(house+facade -> Table1[Facade Price])
   c. Design Guidelines  = SUM(estate requirements M24:M50) [- $4,620 if no corner]
   d. Extra Landscaping  = MAX(0, (lot_size - house_lot_total)) * $39/sqm
   e. Upgrades           = SUM(auto-selected upgrades Y24:Y50)
                           - HPS exclusion - facade exclusion + KDRB surcharge
   f. Discounts          = $5K if small lot/regional, $3K if Dwellings group
   g. FBC escalation     = if contract > 30 days out, apply % escalation
   h. Holding costs      = if 10/90 deal, 10% of build price

4. BUILD PRICE ASSEMBLY:
   Components = House + Facade + Site Costs + Guidelines + Landscaping
                + Upgrades + Discounts + Comms Adjustment
   Build Price = ROUNDUP(Components - base_commission + FBC, -2) + Guidelines

5. PACKAGE PRICE:
   If fixed commission:  Package = Land + Build
   If % commission:      Package = ROUNDUP((Land + Build) / 0.934, -2)

6. VALIDATION:
   - House Fits? = check lot dimensions >= house minimum dimensions
   - Facade check = validate facade is allowed for estate
   - FBC % displayed for transparency

7. OUTPUT -> Tender document auto-generated from Pricing Sheet values
```

---

## 5. Data Volumes

| Entity | Row Count | Unique Keys |
|--------|-----------|------------|
| House designs | 356 facade combos | 57 unique houses |
| Energy ratings | 1,120 | 70 houses x 16 orientations |
| FBC escalation | 36 bands | N/A |
| Sales estimators | 8 | N/A |
| Upgrades (HH) | ~190 | ~150 actual items |
| Upgrades (KBC) | 2 | 2 |
| Upgrades (KTH) | 29 | 29 |
| Estates | 4,785 | 861 unique estates |
| Suburbs | N/A | 241 unique |
| Developers | N/A | 236 unique |
| Travel surcharges | 155 | Suburb-based |
| Postcodes (rock costs) | 57 | Postcode-based |
| BDMs | 9 | N/A |
| Wholesale groups (total) | ~482 across all BDMs | Many overlap |
| Site cost line items | ~30 per tier x 3 tiers | ~90 total |
| KBC houses | 44 combos | ~8 unique |

---

## 6. Gaps vs Current 20-Table PostgreSQL Schema

### Current schema tables:
1. `regions` -- Has name only; missing suburb-to-region mapping
2. `developers` -- OK but missing contact info from ESTATES
3. `estates` -- Has contact info; **missing design guideline columns (10-36)**
4. `estate_stages` -- Has name and status; missing POS number
5. `stage_lots` -- Good lot structure but **missing**: street_name used differently, no batch pricing support
6. `house_packages` -- Tracks assigned designs but not pricing catalog
7. `pricing_requests` -- Good workflow model
8. `pricing_templates` -- Template metadata only
9. `global_pricing_rules` -- Has cell_row/cell_col (Excel-centric); no semantic structure
10. `stage_pricing_rules` -- Same Excel-centric approach
11. `pricing_rule_categories` -- Good concept
12. `profiles` -- User accounts
13. `user_roles` -- Role assignments
14. `clash_rules` -- Facade clashing
15. `configurations` -- Data source configs
16. `ingestion_logs` -- Import tracking
17. `notifications` -- Alerts
18. `filter_presets` -- Saved searches
19. `status_history` -- Lot status tracking
20. `estate_documents` -- File attachments

### Critical gaps:

#### Missing entities:
1. **`house_designs`** -- No table for the house catalog (57 designs with dimensions, floor area, squares, details)
2. **`house_facades`** -- No table for facade options per house (356 combos with prices)
3. **`energy_ratings`** -- No table for the 1,120 orientation/star-rating records
4. **`upgrades`** -- No table for the ~190 upgrade specifications with prices and categories
5. **`wholesale_groups`** -- No table for the ~482 BDM-to-group commission mappings
6. **`bdm_profiles`** (or extend `profiles`) -- No BDM concept
7. **`travel_surcharges`** -- No suburb-to-surcharge lookup
8. **`postcode_costs`** (rock removal) -- No postcode-to-cost mapping
9. **`site_cost_matrix`** -- No representation of the 3-tier, 8-band site cost grid
10. **`fbc_escalation`** -- No table for the day-range-to-percentage escalation bands
11. **`estate_guidelines`** -- The 27 design guideline columns per estate (cols 10-36) have no relational equivalent

#### Structural issues:
1. **Pricing rules are Excel-centric** -- `global_pricing_rules` and `stage_pricing_rules` use `cell_row`/`cell_col` references which tie them to the Excel layout. They should store business-semantic data (item_name, condition_type, condition_value, cost).
2. **No house-facade relationship** -- The current `house_packages` table tracks lot assignments but doesn't model the catalog of available house+facade combinations.
3. **Estate guidelines are not normalized** -- The ESTATES sheet stores 27 guideline cost columns per estate-stage. The current schema has no equivalent. These should be an `estate_guideline_items` junction table (estate_stage_id, guideline_type_id, cost, override_text).
4. **Commission structure missing** -- No representation of the BDM -> wholesale group -> commission amount hierarchy.
5. **No brand separation** -- Current `Brand` enum has Hermitage/Kingsbridge but no separate house catalogs. The Excel has separate Table1 (HH) and Table118 (KBC) with different prices.
6. **Site costs not modeled** -- The complex 3-tier, size-banded, condition-driven site cost matrix has no database equivalent. `StagePricingRule` is too flat.
7. **POS number** is on `stage_lots` but in the Excel it's per estate-stage in ESTATES.
8. **Suburb includes postcode** in Excel (e.g., "Clyde North 3978") but current schema separates them.

#### What's working well:
- Estate -> Stage -> Lot hierarchy matches the Excel's ESTATES structure
- Lot dimensions (frontage, depth, size, corner_block, orientation, easements) are well-modeled
- Status tracking and history are good additions not in the Excel
- Pricing request workflow is a good addition

---

## 7. Proposed Entity Additions for Database Redesign

### New tables needed:

```sql
-- House design catalog (denormalized from Table1)
house_designs (
    design_id SERIAL PK,
    brand VARCHAR(100),        -- 'Hermitage Homes' or 'Kingsbridge Complete'
    house_name VARCHAR(100),   -- 'Access 18 HPS'
    base_price NUMERIC(10,2),  -- 390000
    storey VARCHAR(10),        -- 'Single' or 'Double'
    frontage NUMERIC(6,2),     -- 10.5
    depth NUMERIC(6,2),        -- 28
    gf_sqm NUMERIC(8,2),       -- 128.54
    total_sqm NUMERIC(8,2),    -- 167.48
    lot_total NUMERIC(10,2),   -- GENERATED: frontage * depth
    squares INTEGER,           -- 18
    details TEXT,              -- '3 Bed, 3 Bath...'
    effective_date DATE,
    UNIQUE(brand, house_name)
)

-- Facade options per house design
house_facades (
    facade_id SERIAL PK,
    design_id INTEGER FK -> house_designs,
    facade_name VARCHAR(100),  -- 'Holt'
    facade_price NUMERIC(10,2),-- 0 for 'Included', otherwise dollar amount
    facade_details TEXT,
    UNIQUE(design_id, facade_name)
)

-- Energy star ratings
energy_ratings (
    rating_id SERIAL PK,
    design_id INTEGER FK -> house_designs,
    garage_side VARCHAR(10),   -- 'Left' or 'Right'
    orientation VARCHAR(5),    -- 'N','NE','E','SE','S','SW','W','NW'
    star_rating NUMERIC(3,1),  -- 7.3
    best_worst VARCHAR(1),     -- 'B' or 'W'
    compliance_cost NUMERIC(10,2), -- 5000/8000/15000
    UNIQUE(design_id, garage_side, orientation)
)

-- Upgrade catalog
upgrade_items (
    upgrade_id SERIAL PK,
    brand VARCHAR(100),
    category VARCHAR(50),       -- 'PACKS','EXTERNALS','INTERNALS', etc.
    description TEXT,
    price NUMERIC(10,2),        -- can be negative for downgrades
    date_added DATE,
    notes TEXT,
    sort_order INTEGER
)

-- BDM commission schedules
wholesale_groups (
    group_id SERIAL PK,
    bdm_profile_id INTEGER FK -> profiles,
    group_name VARCHAR(255),
    commission_fixed NUMERIC(10,2),  -- NULL if percentage
    commission_pct NUMERIC(5,4),     -- NULL if fixed
    gst_registered BOOLEAN,
    UNIQUE(bdm_profile_id, group_name)
)

-- Travel surcharge by suburb
travel_surcharges (
    surcharge_id SERIAL PK,
    suburb VARCHAR(100),        -- 'Ballarat 3350'
    surcharge NUMERIC(10,2),    -- 8000
    region VARCHAR(50)          -- 'Ballarat'
)

-- Postcode-based rock removal costs
postcode_costs (
    postcode VARCHAR(10) PK,
    rock_removal_cost NUMERIC(10,2)
)

-- Estate design guidelines (replaces 27 columns per estate-stage)
guideline_types (
    type_id SERIAL PK,
    description TEXT,           -- full specification text (column header)
    short_name VARCHAR(100),    -- '3rd_pipe', 'eaves_1500', etc.
    sort_order INTEGER
)

estate_guidelines (
    guideline_id SERIAL PK,
    estate_id INTEGER FK -> estates,
    stage_id INTEGER FK -> estate_stages,
    type_id INTEGER FK -> guideline_types,
    cost NUMERIC(10,2),         -- dollar cost
    override_text TEXT,         -- text override of the guideline spec
    UNIQUE(estate_id, stage_id, type_id)
)

-- FBC escalation bands
fbc_escalation (
    band_id SERIAL PK,
    day_start INTEGER,          -- 30
    day_end INTEGER,            -- 59
    multiplier NUMERIC(5,4),    -- 1.003
    brand VARCHAR(100)
)

-- Site cost matrix (3 tiers x N line items x 8 size bands)
site_cost_tiers (
    tier_id SERIAL PK,
    tier_name VARCHAR(50),      -- '0-1000mm', '1001-1500mm', '1501-2000mm'
    fall_min_mm INTEGER,
    fall_max_mm INTEGER
)

site_cost_items (
    item_id SERIAL PK,
    tier_id INTEGER FK -> site_cost_tiers,
    item_name VARCHAR(255),
    condition_formula TEXT,      -- human-readable condition
    cost_single_lt190 NUMERIC(10,2),
    cost_double_lt190 NUMERIC(10,2),
    cost_single_191_249 NUMERIC(10,2),
    cost_double_191_249 NUMERIC(10,2),
    cost_single_250_300 NUMERIC(10,2),
    cost_double_250_300 NUMERIC(10,2),
    cost_single_300plus NUMERIC(10,2),
    cost_double_300plus NUMERIC(10,2),
    sort_order INTEGER
)
```

### Relationships to add to existing tables:

```sql
-- estates: add guideline-related fields
ALTER TABLE estates ADD COLUMN pos_number VARCHAR(20);

-- stage_lots: already good, but ensure:
--   - street_name is populated
--   - orientation matches the 8 compass values
--   - corner_block is used consistently

-- profiles: add BDM flag or role
-- (already has user_roles table, just need 'bdm' role type)
```

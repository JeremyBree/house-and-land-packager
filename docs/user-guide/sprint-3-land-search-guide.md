# Land Search & Saved Presets — Sprint 3

This guide walks through the Land Search Interface (LSI) shipped in
Sprint 3: cross-estate filtering, saved filter presets, and CSV /
XLSX exports.

It assumes you are already logged in. Any authenticated role can
use Land Search — no admin or pricing privilege required.

## Opening Land Search

1. Sidebar → **Land Search**.
2. The page opens with a filter panel on the left and a result grid
   on the right.
3. By default, the grid loads with `Status = Available` applied and
   results sorted by **land price** (ascending).

## Filter Panel

Filters are grouped into sections. Any combination is valid; filters
AND across sections, and OR within multi-select lists.

### Location

- **Estates** — pick one or more estates.
- **Developers** — pick one or more developers.
- **Regions** — pick one or more regions.
- **Suburbs** — match lots whose estate is in any of the listed
  suburbs.

### Status

- **Statuses** — multi-select across `Available`, `Unavailable`,
  `Hold`, `Deposit Taken`, `Sold`. The default value is
  **Available** — clear it to include everything.

### Price

- **Min / Max land price** — both optional.
- **Exclude lots with no price** — when ticked, filters out lots
  whose `land_price` has not been entered yet. On by default for
  most day-to-day searches.

### Size

- **Min / Max size (m²)** — both optional.

### Dimensions

- **Min frontage (m)** — optional.
- **Min depth (m)** — optional.
- **Corner block only** — tick to restrict to corner blocks; leave
  unticked to include everything.

### Title Date

- **Title date from / to** — match lots with a title date inside
  the range.

### Text Search

A single search box that does a case-insensitive substring match
across **lot number**, **estate name**, **suburb**, and **developer
name**. Useful for quick estate / developer lookup without touching
the dropdowns.

## Sorting & Pagination

- Sort by: `land_price`, `size_sqm`, `frontage`, `lot_number`,
  `estate_name`, or `last_confirmed_date`.
- Toggle ascending / descending in the column header.
- Page size defaults to **50**; maximum **200**.

## Saving a Filter Preset

Presets are **per-user**. Each user has their own namespace — your
presets are invisible to other consultants.

1. Configure the filter panel exactly as you want it.
2. Click **Save preset**.
3. Enter a name (1-255 characters). Examples:
   - `Budget Lots <$400k`
   - `Corner Blocks North`
   - `Titled This Quarter — Stockland`
4. Click **Save**.

Preset names must be unique **within your account**. If you try to
save under a name you already use, you'll be asked to pick a new
one (or overwrite the existing preset).

## Loading a Filter Preset

1. Click **Load preset** in the filter panel.
2. Choose from your saved presets.
3. The filter panel populates and the results refresh immediately.

## Renaming / Deleting a Preset

- **Rename**: open the preset menu → **Rename**.
- **Replace filters**: load the preset, adjust filters, then
  **Save preset** under the same name.
- **Delete**: open the preset menu → **Delete**.

## Exporting Results

Two export formats are available; both export the **currently
filtered** result set (ignoring the paging — you get every row
that matches, up to the cap).

### CSV

Best for spreadsheets, further analysis, or importing into other
tools. Plain UTF-8, comma-separated, header row included.

1. Apply your filters.
2. Click **Export → CSV**.
3. The file downloads as `lots_export_YYYYMMDD_HHMMSS.csv`.

### XLSX (formatted)

Best for printing and sending to stakeholders. The workbook ships
with:

- A bold, frozen header row.
- Currency columns (`land_price`, `build_price`, `package_price`)
  formatted as currency.
- Sensible column widths.

1. Apply your filters.
2. Click **Export → XLSX**.
3. The file downloads as `lots_export_YYYYMMDD_HHMMSS.xlsx`.

### Export Limits

- **Maximum 5000 rows** per export.
- If your filters match more than 5000 lots, the export will fail
  with a **"Export too large"** message — no partial file is
  produced. **Narrow your filters** (add a status, a price ceiling,
  or an estate selection) and try again.
- The cap is enforced server-side **before** the file is built, so
  over-limit exports fail fast.

## Tips

- **Start narrow, widen as needed.** Applying even one or two
  filters (status + price) dramatically cuts result size and makes
  scanning the grid easier.
- **Use text search for quick estate lookup.** Typing the estate
  name into the text-search box is often faster than opening the
  estates dropdown.
- **Combine presets with text search.** Load a broad preset (e.g.
  `Budget Lots <$400k`) and then narrow further with text search or
  a suburb filter — the text-search input doesn't overwrite your
  loaded preset.
- **Exclude null prices** when comparing on price. Leaving them in
  can put unpriced lots at the top when sorting ascending.

## Coming in Sprint 4

- **Clash rules** — developer-specific package-build restrictions.
- **Packages** — house-plus-land package composition built on top
  of the lots you find in LSI.

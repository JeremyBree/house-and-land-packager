# Sprint 3 Release Notes

**Release date:** 2026-04-06
**Environment:** Railway PoC
**URL:** https://house-and-land-packager-production.up.railway.app
**Repository:** https://github.com/JeremyBree/house-and-land-packager

## Sprint Goal

Deliver the **Land Search Interface (LSI)** — a cross-estate lot
search with 14 filters, sortable paginated results, per-user saved
filter presets, and CSV / XLSX exports. This is the first
consultant-facing feature that reaches across all estates.

## What's New (User-Facing)

- **Land Search Interface.** A sidebar-accessible page for
  consultants to filter every lot in the system by location
  (estate, developer, region, suburb), status, price range, size
  range, frontage, depth, corner block, title date range, and a
  free-text search across lot number / estate / suburb / developer.
- **Sorting & pagination.** Results sort by land price, size,
  frontage, lot number, estate name, or last confirmed date, up to
  200 rows per page.
- **Default "Available" view.** LSI opens with `Status = Available`
  pre-applied and results sorted by land price ascending.
- **Exclude-null-price toggle.** Keep unpriced lots out of
  price-sorted comparisons with one click.
- **Saved filter presets.** Each consultant can save, name, load,
  rename, and delete their own filter combinations — `Budget Lots
  <$400k`, `Corner Blocks North`, etc. Presets are **per-user**.
- **CSV export.** One-click download of the current result set as a
  plain UTF-8 CSV.
- **XLSX export (formatted).** One-click download of the current
  result set as an openpyxl workbook, with a bold frozen header and
  currency-formatted price columns.

## Technical Additions

### Backend

- **`LotSearchRepository`** (`src/hlp/repositories/lot_search_repository.py`)
  — dynamic filter-builder that JOINs `stage_lots` to
  `estate_stages`, `estates`, `developers`, and `regions` and
  applies filters conditionally. Provides `search`, `search_all`,
  and `count` for the paginated view, export streaming, and the
  pre-export cap check.
- **`ExportService`** (`src/hlp/shared/export_service.py`) — CSV
  serialization plus openpyxl-based XLSX generation. XLSX output
  has a bold frozen header row and currency number format on
  `land_price`, `build_price`, and `package_price`.
- **LSI router** (`src/hlp/api/routers/lot_search.py`) —
  `POST /api/lots/search`, `POST /api/lots/export/csv`,
  `POST /api/lots/export/xlsx`. Enforces the 5000-row export cap
  before streaming.
- **Filter preset router** (`src/hlp/api/routers/filter_presets.py`)
  — user-scoped CRUD: `GET/POST/GET/PATCH/DELETE
  /api/filter-presets[/preset_id]`. All endpoints ownership-check
  against the caller's `profile_id`.
- **New exceptions**: `ExportTooLargeError` (413),
  `FilterPresetNotFoundError` (404), `DuplicatePresetNameError`
  (409).

### API Endpoints Added

8 new endpoints across 2 routers. Full reference:
**`docs/api/sprint-3-endpoints.md`**.

- Lot search & export (3): search, export CSV, export XLSX
- Filter presets (5): list, create, get, patch, delete

### Data Model

One new table. No migration was required — the lifespan hook's
`Base.metadata.create_all()` populates it alongside the existing
tables:

- `filter_presets` — `(preset_id, profile_id, name, filters jsonb,
  created_at, updated_at)`, unique on `(profile_id, name)`. See
  ADR-005.

### Performance Notes

- Search uses SQLAlchemy `joinedload` / explicit joins to avoid
  N+1 when hydrating enriched fields (`estate_name`,
  `developer_name`, `region_name`, `stage_name`).
- Column indexes on `stage_lots.status`, `stage_lots.land_price`,
  and `stage_lots.size_sqm` back the common filter/sort paths.
- Export uses an up-front `count()` against the filtered query so
  over-limit requests fail fast at 413 without materializing a
  partial file.

## Known Limitations

- **Export cap at 5000 rows.** Over-cap exports fail with 413 — no
  partial file, no "first 5000" fallback. This is deliberate to
  prevent silent truncation, but means large exports must be
  narrowed by the user.
- **No signed-URL exports.** Export responses stream through the
  FastAPI service. Acceptable for PoC scale; production will move
  to signed storage URLs alongside the Azure Blob migration
  (ADR-003).
- **No email delivery of exports.** Exports are synchronous
  downloads only. No "email me the file" workflow yet.
- **Presets have no structural migration.** Renaming a filter field
  will silently drop that filter from old presets on load — see
  ADR-005 for mitigation.
- **No shared / team presets.** Presets are strictly per-user.
- **No frontend production deploy yet** (carried from Sprint 2) —
  the SPA is still served out of the Railway API service.

## Breaking Changes

None — additive release.

## Links

- **API reference:** `docs/api/sprint-3-endpoints.md`
- **User guide:** `docs/user-guide/sprint-3-land-search-guide.md`
- **Acceptance criteria:** `docs/testing/sprint-3-acceptance-criteria.md`
- **ADR-005** (Saved filter presets): `docs/adr/005-saved-filter-presets.md`

## What's Next

**Sprint 4 — Clash rules + packages.** Developer-specific build
restrictions (clash rules) and the first cut of house-plus-land
package composition built on top of the lots surfaced by LSI.

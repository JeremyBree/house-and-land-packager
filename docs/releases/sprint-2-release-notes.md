# Sprint 2 Release Notes

**Release date:** 2026-04-05
**Environment:** Railway PoC
**URL:** https://house-and-land-packager-production.up.railway.app
**Repository:** https://github.com/JeremyBree/house-and-land-packager

## Sprint Goal

Deliver the **stage / lot lifecycle** with a full status audit trail
and volume-backed **file storage** for estate documents. This unlocks
every downstream workflow (Land Search, Packages, Pricing) that
depends on lot-level data.

## What's New (User-Facing)

- **Stages under estates.** Admins can add, edit, and delete stages
  on each estate, with planned lot count, status (Active / Upcoming /
  Completed), and release date.
- **Stage lots.** Admins can add lots individually, in a bulk JSON
  payload, or by uploading a CSV file. Lot uniqueness is enforced per
  stage.
- **CSV upload for lots** with documented column format, boolean/
  decimal/date parsing, and duplicate-skipping semantics.
- **Lot status lifecycle.** Admin and pricing users can transition a
  lot's status through `Available`, `Unavailable`, `Hold`, `Deposit
  Taken`, `Sold`, with a required reason.
- **Full status history.** Every transition (including refreshes
  where the status is unchanged) is recorded with previous status,
  new status, timestamp, triggering agent, and reason.
- **Estate documents.** Admins can upload PDFs, DOCs, and images (≤10
  MB) against an estate or stage. Any authenticated user can
  download.
- **Stage detail statistics.** The stage detail endpoint now returns
  `lot_count_actual` and a `status_breakdown` keyed by LotStatus.

## Technical Additions

### Backend

- **`StorageService`** (`src/hlp/shared/storage_service.py`) —
  volume-backed file storage wrapper. Three categories
  (`estate-documents`, `package-flyers`, `generated-sheets`), UUID-
  prefixed filenames, path-escape guards. See ADR-003.
- **CSV parser** (`src/hlp/shared/lot_service.py`) — UTF-8-BOM-safe
  `csv.DictReader`-based parser with typed coercion for decimals,
  dates, booleans; all-or-nothing parse semantics; 1-indexed row
  errors.
- **Status transition service** — `transition_lot_status` writes a
  `status_history` row, updates `status` and `last_confirmed_date`,
  and tags the row with `manual:{email}`. See ADR-004.
- **Document service** — size/type validation (10 MB, PDF/DOC/DOCX/
  PNG/JPG/JPEG), writes via `StorageService`, creates the
  `estate_documents` row.
- **Role dependency `require_roles(...)`** — used by the lot-status
  endpoint to allow both admin **and** pricing.

### API Endpoints Added

19 new endpoints across 4 routers. Full reference:
**`docs/api/sprint-2-endpoints.md`**.

- Stages (5): list, create, get (with stats), patch, delete
- Lots (9): list, create, bulk, CSV upload, get, patch, delete,
  status transition, status history
- Documents (4): upload, list, download, delete
- Files (1): volume-backed file serving

### Data Model

No migration was required. The lifespan hook's
`Base.metadata.create_all()` populates the Sprint 2 tables alongside
the Sprint 1 tables (all 19 still present in the schema from day one):

- `estate_stages`
- `stage_lots`
- `status_history`
- `estate_documents`

### Seed Expansion

The dev seed now inserts **~25 stages** distributed across the
existing estates, and **~250 lots** with VIC-realistic dimensions
(12.5-16m frontages, 400-550 m² sizes) and prices (land $350k-$450k,
packages $650k-$800k), spread across all five `LotStatus` values.
Empty-DB auto-seed still runs on first boot (ADR-002 unchanged).

## Known Limitations

- **Single-replica storage.** The Railway volume is bound to one
  service replica; the PoC cannot scale out horizontally while
  keeping document access consistent. Production will migrate to
  Azure Blob (ADR-003).
- **No volume backups.** The Railway volume is **not** automatically
  snapshotted — see the document-storage runbook for operational
  guidance.
- **No signed URLs or CDN.** Every document fetch is a round-trip
  through the FastAPI service.
- **CSV upload is all-or-nothing on parse.** A single bad row rejects
  the whole file. Operators need to fix and re-upload.
- **Status history grows unbounded.** No archival strategy yet.
  Acceptable for the PoC's row volume.
- **No password reset** (carried from Sprint 1).
- **No frontend production deploy yet** — the SPA is still served
  out of the Railway API service.

## Breaking Changes

None — additive release.

## Links

- **API reference:** `docs/api/sprint-2-endpoints.md`
- **CSV upload guide:** `docs/operations/runbooks/sprint-2-csv-upload-guide.md`
- **Document storage runbook:** `docs/operations/runbooks/sprint-2-document-storage.md`
- **User guide:** `docs/user-guide/sprint-2-managing-lots.md`
- **Acceptance criteria:** `docs/testing/sprint-2-acceptance-criteria.md`
- **ADR-003** (Railway volume storage): `docs/adr/003-railway-volume-storage.md`
- **ADR-004** (Status transition history): `docs/adr/004-status-transition-history.md`

## What's Next

**Sprint 3 — Land Search Interface + Exports.** Cross-estate search
and filtering over all active lots, a saved-view mechanism, and CSV
export of the result set.

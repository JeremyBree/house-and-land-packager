# Sprint 4 Release Notes

**Release date:** 2026-04-05
**Environment:** Railway PoC
**URL:** https://house-and-land-packager-production.up.railway.app
**Repository:** https://github.com/JeremyBree/house-and-land-packager

## Sprint Goal

Deliver **clash rules**, **house packages**, and **conflict
detection** — the core features that prevent duplicate house designs
on adjacent lots and let admins compose house-plus-land packages
tied to specific lots.

## What's New (User-Facing)

- **Clash rules.** Admins can define per-lot restrictions within an
  estate + stage scope: "Lot 101 cannot match Lot 102". Rules are
  **bidirectional** — creating one direction automatically creates
  the reverse. Rules can be copied between stages for fast
  onboarding of new releases.
- **House packages.** Full CRUD for house-plus-land packages. Each
  package ties a lot to a design, facade, colour scheme, and builder
  brand. Packages are filterable by estate, stage, brand, design,
  facade, and lot number, with paginated results.
- **Flyer upload.** Admins can attach a PDF or image flyer to any
  package and remove it later.
- **Conflict detection.** A read-only view that scans all packages
  against clash rules and surfaces violations:
  - **High** severity: two packages on clashing lots share the same
    design + facade.
  - **Critical** severity: same design + facade **and** same colour
    scheme.
- **Conflict summary.** Dashboard-ready aggregates: total conflict
  count, breakdown by type, and breakdown by estate.

## Technical Additions

### Backend

- **`clash_service`** (`src/hlp/shared/clash_service.py`) —
  bidirectional enforcement on create and update, stage-to-stage
  copy, restricted-lot lookup, and within-submission validation.
  Deduplicates `cannot_match` lists via `dict.fromkeys`.
- **`conflict_service`** (`src/hlp/shared/conflict_service.py`) —
  on-demand conflict detection. Compares packages across clashing
  lots using case-insensitive design + facade matching. Deduplicates
  conflicts by sorted `(package_a_id, package_b_id)` pair to
  prevent duplicates from bidirectional rules.
- **`package_service`** (`src/hlp/shared/package_service.py`) —
  package CRUD and flyer upload/delete. Flyer storage uses the
  existing Railway volume path (ADR-003).
- **Clash rules router** (`src/hlp/api/routers/clash_rules.py`) —
  four sub-routers covering estate-scoped, stage-scoped,
  estate+stage-scoped, and direct rule-ID operations.
- **Packages router** (`src/hlp/api/routers/packages.py`) — CRUD,
  filtered list with pagination, flyer upload and delete.
- **Conflicts router** (`src/hlp/api/routers/conflicts.py`) — list
  conflicts (optionally by estate) and summary.
- **New exceptions**: `ClashRuleNotFoundError` (404),
  `PackageNotFoundError` (404).

### API Endpoints Added

16 new endpoints across 3 routers. Full reference:
**`docs/api/sprint-4-endpoints.md`**.

- Clash rules (7): list by estate, list by stage, create, get,
  update, delete, copy
- Packages (7): list, create, get, update, delete, upload flyer,
  delete flyer
- Conflicts (2): list, summary

### Data Model

Two new tables. No migration was required — the lifespan hook's
`Base.metadata.create_all()` populates them alongside existing
tables:

- `clash_rules` — `(rule_id, estate_id, stage_id, lot_number,
  cannot_match jsonb, created_at)`, unique on `(estate_id, stage_id,
  lot_number)`.
- `house_packages` — `(package_id, estate_id, stage_id, lot_number,
  design, facade, colour_scheme, brand, source, status, flyer_path,
  created_at, updated_at)`.

### Performance Notes

- Conflict detection caches package lookups by `(estate_id,
  stage_id, lot_number)` to avoid repeated DB queries during the
  scan.
- Clash rule copy uses bulk upsert to minimize round-trips.
- Package list uses conditional filter application — only non-null
  filters generate WHERE clauses.

## Known Limitations

- **Clash rule deletion is unilateral.** Deleting a rule for lot A
  does not automatically remove lot A from lot B's `cannot_match`
  list. Admins must manage both sides explicitly.
- **Conflict detection is compute-on-read.** At PoC scale this is
  sub-millisecond, but will need a materialized cache if rule/package
  counts grow past ~1000.
- **No conflict push notifications.** Admins must navigate to the
  conflicts page or dashboard to see new conflicts.
- **No conflict history/audit trail.** Conflicts are computed live;
  there is no record of when a conflict first appeared or was
  resolved.
- **Flyer storage uses Railway volumes.** Production will move to
  Azure Blob Storage (ADR-003).
- **No frontend production deploy yet** (carried from Sprint 2) —
  the SPA is still served out of the Railway API service.

## Breaking Changes

None — additive release.

## Links

- **API reference:** `docs/api/sprint-4-endpoints.md`
- **User guide:** `docs/user-guide/sprint-4-clash-rules-and-packages.md`
- **Acceptance criteria:** `docs/testing/sprint-4-acceptance-criteria.md`
- **ADR-006** (Bidirectional clash rules): `docs/adr/006-bidirectional-clash-rules.md`
- **ADR-007** (Client-cacheable conflict detection): `docs/adr/007-conflict-detection-client-side.md`

## What's Next

**Sprint 5** — TBD. Likely candidates: package submission workflow,
ingestion agent groundwork, or builder portal integration.

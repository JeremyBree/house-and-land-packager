# ADR-005: Per-User JSON Filter Presets

- **Status:** Accepted
- **Date:** 2026-04-06
- **Related:** ADR-001 (JWT auth), Sprint 3 (Land Search Interface)

## Context

The Land Search Interface (LSI) shipped in Sprint 3 exposes 14
filters — location (estate, developer, region, suburb), status,
price range, size range, frontage, depth, corner block, title date
range, null-price exclusion, and free-text search — plus sort and
pagination controls.

Consultants (LSIs) repeatedly apply the same combinations of these
filters during day-to-day work: "budget lots under $400k", "corner
blocks in northern suburbs", "titled lots available this quarter
from developer X". Re-entering 5-8 fields per search is a tax on
every sales conversation.

We need a way to save and recall named filter combinations **per
user**, without a schema-migration cost every time we add or
restructure a filter in the LSI.

## Decision

Store filter presets as JSONB in a single `filter_presets` table,
scoped to `profile_id`.

Schema:

- `preset_id` (PK)
- `profile_id` → `profiles.profile_id` (owner)
- `name` (string, 1-255 chars)
- `filters` (JSONB — serialized `LotSearchFilters`)
- `created_at`, `updated_at`
- **Unique constraint** on `(profile_id, name)`

Presets are exclusively per-user. There is no shared / team / global
preset concept in Sprint 3. Every read, write, update, and delete is
ownership-checked via `profile_id` — accessing another user's preset
returns `404 filter_preset_not_found` rather than `403`, to avoid
leaking existence.

The frontend treats `filters` as an opaque `LotSearchFilters`-shaped
blob. On load it hydrates the LSI filter panel from the JSON and
validates each field against the current schema, ignoring unknown
keys.

## Consequences

### Positive

- **Zero-config for new filters.** Adding a filter to
  `LotSearchFilters` requires no DB migration and no preset-model
  change.
- **Schema-free storage.** Presets remain valid across additive
  schema changes because unknown fields are simply ignored on load.
- **Tight ownership model.** Unique `(profile_id, name)` lets each
  user keep a clean, meaningful namespace (`Budget Lots <$400k`,
  `Corner Blocks North`) without colliding with other users.

### Negative

- **No server-side structural validation.** A stale or malformed
  preset in the DB is only caught by the frontend when it loads. We
  accept this: the LSI already ignores unknown keys, and the blast
  radius of a corrupt preset is one user.
- **Cannot migrate preset structure automatically.** If we rename
  `price_min` → `land_price_min`, old presets will silently lose that
  filter on load. **Mitigation:** the frontend validates preset
  shape on load and ignores unknown fields; any planned rename must
  be handled with explicit compatibility code in the load path.
- **No sharing.** Consultants can't share a "team preset" without
  manually copying filter JSON. Acceptable for the PoC user base
  (~5 LSIs); revisit if demand appears.

### Follow-Ups

- Decide on a sharing model (team presets / global presets) if
  requested post-PoC.
- If we ever need to migrate a filter rename, add a normalize-on-
  load step in the repository layer keyed to a preset `schema_version`.

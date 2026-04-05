# ADR-007: Client-Cacheable Conflict Detection

- **Status:** Accepted
- **Date:** 2026-04-05
- **Related:** ADR-006 (bidirectional clash rules), Sprint 4

## Context

When packages are created for lots that are subject to clash rules,
the system must detect conflicting combinations — two packages on
clashing lots that share the same design + facade (or design +
facade + colour scheme). Conflicts need to be surfaced to admins
quickly so they can resolve them before a build order is placed.

The detection logic is deterministic: given the current set of clash
rules and packages, the conflict list is a pure function of those
inputs. There is no user-specific or session-specific state
involved.

We considered three approaches:

1. **Eager (write-time).** Detect conflicts on every package
   create/update. Rejected: adds latency to writes and complicates
   transaction rollback semantics.
2. **Background job.** Run a periodic scan and cache results.
   Rejected: adds infrastructure complexity (scheduler, cache
   invalidation) disproportionate to PoC scale.
3. **On-demand read endpoint.** Compute conflicts at query time and
   return them. The response is stateless and cacheable by the
   client.

## Decision

Implement conflict detection as a **read-only, on-demand endpoint**
(`GET /api/conflicts`) that computes conflicts at query time by
scanning clash rules against packages.

### Detection algorithm

1. Load all clash rules (optionally filtered by `estate_id`).
2. For each rule, load packages for the rule's lot and for each lot
   in `cannot_match`.
3. For every pair of packages across clashing lots, compare:
   - `design` and `facade` (case-insensitive, trimmed).
   - If both match: **conflict detected**.
4. Determine severity:
   - `design + facade` match only: `conflict_type = "design-facade"`,
     `severity = "high"`.
   - `design + facade + colour_scheme` all match (and colour is
     non-empty): `conflict_type = "design-facade-colour"`,
     `severity = "critical"`.
5. **Deduplicate by sorted package-ID pair.** Each conflict is
   identified by `tuple(sorted([package_a.id, package_b.id]))`.
   This prevents the same conflict from appearing twice when the
   bidirectional rules cause both directions to be scanned.

### Client cacheability

- The endpoint returns a plain JSON list. The client can cache the
  result and poll at an interval appropriate to its use case (e.g.
  refresh on page load, or poll every 60 seconds on the dashboard).
- No server-side cache, ETag, or push mechanism is implemented. At
  PoC scale (~200 packages, ~50 rules), the scan completes in
  single-digit milliseconds.

### Summary endpoint

`GET /api/conflicts/summary` returns aggregate counts
(`total_conflicts`, `by_type`, `by_estate`) for dashboard widgets
without transferring the full conflict list.

## Consequences

### Positive

- **Zero write-path overhead.** Package CRUD is unaffected by
  conflict detection; no transactional coupling.
- **Deterministic and reproducible.** The same data always produces
  the same conflict list — no stale-cache bugs.
- **Simple implementation.** One service function, two endpoints, no
  background infrastructure.
- **Client-friendly.** The frontend can cache, debounce, or poll
  without server-side session state.

### Negative

- **Compute-on-read scales linearly.** With R rules and P packages,
  worst-case is O(R * P^2). Acceptable at PoC scale; will need
  indexing or materialized results if rule/package counts grow past
  ~1000.
- **No push notification.** Admins must navigate to the conflicts
  page or dashboard to see new conflicts. A WebSocket or SSE push
  may be added post-PoC if real-time alerting is requested.
- **No conflict history.** Conflicts are computed live; there is no
  record of when a conflict first appeared or was resolved. Add an
  audit trail if compliance requires it.

### Follow-Ups

- Add a materialized conflict table with write-time invalidation if
  scan latency exceeds 500ms at production scale.
- Consider a WebSocket channel that pushes conflict-count deltas to
  connected dashboard clients.
- Evaluate adding `ETag` / `Last-Modified` headers based on the
  latest `package.updated_at` timestamp to support HTTP-level
  caching.

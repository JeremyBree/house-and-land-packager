# ADR-004: Append-Only Status History for Lot Transitions

- **Status:** Accepted
- **Date:** 2026-04-05
- **Related:** ADR-001 (JWT auth), Sprint 7 (ingestion agent, planned)

## Context

A lot's status (`Available`, `Unavailable`, `Hold`, `Deposit Taken`,
`Sold`) is the single most operationally important field in the
system: it drives the Land Search Interface, package availability,
sales conversations, and the ingestion-agent workflows planned for
Sprint 7.

Every change to a lot's status must be auditable — who (or what)
changed it, when, from what, to what, and why. The audit trail also
has to survive a lot being updated by multiple sources (manual user
action, email ingestion, portal scrape) without losing any transition.

Sprint 7's ingestion agent additionally needs to reason over history
to implement the **"absent from feed"** rule: if a lot disappears from
an external feed for N days, infer it was sold or withdrawn. That
inference relies on reading previous transitions and their triggering
agents, not just the current status.

## Decision

Introduce an **append-only** `status_history` table. Every lot
transition inserts one new row. Rows are never updated or deleted by
application code.

Schema highlights (`status_history` table):

- `history_id` (PK)
- `lot_id` → `stage_lots.lot_id`
- `previous_status` (nullable — null for the lot's first-ever
  recorded status)
- `new_status`
- `changed_at` (UTC timestamp)
- `triggering_agent` — free-text discriminator identifying the actor
- `source_detail` — operator-supplied reason (manual) or provenance
  blob (agents)

The `transition_lot_status` service function in
`src/hlp/shared/lot_service.py`:

1. Inserts a row into `status_history` with the **previous** and
   **new** status.
2. Updates `stage_lots.status` to the new value.
3. Updates `stage_lots.last_confirmed_date` to the transition
   timestamp.

**Refreshes are recorded.** Calling `transition_lot_status` with
`new_status == current_status` still creates a history row. This is
deliberate: it records the "we re-confirmed this lot as still
Available today" event that the ingestion agent depends on.

### Triggering agent format

| Source | `triggering_agent` value | Introduced |
|---|---|---|
| Manual user action | `manual:{user_email}` | Sprint 2 |
| Email ingestion agent | `email-agent` | Sprint 7 |
| Portal scraper | `scraper-agent` | Sprint 7 |
| Website scraper | `website-agent` | Sprint 7 |
| System reconciliation | `system:{job_name}` | TBD |

The `manual:{email}` prefix lets us identify, at a glance, which human
made the change — and, critically, distinguishes human input from
agent input when applying conflict-resolution rules.

## Consequences

### Positive

- **Complete audit trail.** Every transition, including refreshes, is
  recoverable.
- **Supports Sprint 7 logic directly.** The ingestion agent can
  compute `days_since_last_confirmed` and `last_source_type` from a
  single query against `status_history`.
- **Simple mental model.** There is one way to change a lot's status
  — call `transition_lot_status` — and doing so always leaves a
  trail.
- **No migration needed for new source types.** Sprint 7 just starts
  writing new `triggering_agent` values.

### Negative

- **Table grows unbounded.** With ~250 lots and daily refreshes from
  multiple sources, we expect roughly 250 × 3 sources × 365 days ≈
  275k rows/year. Manageable for the PoC; will need archival
  (partition by year, move to cold storage) before going to scale.
- **Refresh inserts are chatty.** Every re-confirmation writes a row,
  even when nothing changed. Acceptable trade-off for auditability.
- **No enum-level constraint on `triggering_agent`.** The value is a
  free-form string. We accept this to avoid schema changes every time
  a new agent type is added; formats are documented here instead.

### Follow-Ups

- Add archival strategy (quarterly partition + cold storage) before
  production cutover.
- Add a composite index `(lot_id, changed_at DESC)` if history lookups
  become slow.
- Consider a redacted "audit log" read endpoint that exposes history
  to sales/requester roles without exposing `triggering_agent` user
  emails.

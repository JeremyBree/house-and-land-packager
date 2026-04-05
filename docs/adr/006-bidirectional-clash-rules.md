# ADR-006: Bidirectional Enforcement for Clash Rules

- **Status:** Accepted
- **Date:** 2026-04-05
- **Related:** ADR-004 (status history), Sprint 4 (clash rules + packages)

## Context

Clash rules prevent two adjacent or proximate lots from being built
with the same design + facade combination. A developer submits a
rule such as "Lot 101 cannot match Lot 102 in Stage 1A of Aurora
Rise". In practice, this restriction is inherently symmetric: if Lot
101 cannot look like Lot 102, then Lot 102 cannot look like Lot 101.

Requiring admins to enter both directions manually is error-prone
and doubles the rule-management workload. A single-direction rule
that silently fails to enforce in reverse would create a false sense
of compliance.

Clash rules are scoped to `(estate_id, stage_id)`. Rules do not
cross estate or stage boundaries because developer design guidelines
are always scoped to a specific estate stage release.

## Decision

**Automatically create and maintain reciprocal rules.** When an
admin creates a rule stating "Lot A cannot match Lot B", the service
layer (`clash_service.create_clash_rule`) upserts a reciprocal rule
for each lot in the `cannot_match` list, adding the source lot to
the reciprocal's `cannot_match` array. The same reciprocal-sync
logic runs on update (`clash_service.update_clash_rule`).

Implementation details:

- **Upsert, not duplicate.** If a reciprocal rule already exists for
  that `(estate_id, stage_id, lot_number)`, the source lot is
  appended to the existing `cannot_match` list (deduplicated).
- **Self-exclusion.** A lot is never added to its own `cannot_match`
  list.
- **Deduplication.** `cannot_match` lists are deduplicated by
  preserving insertion order (`dict.fromkeys`), keeping the list
  compact and predictable.
- **Copy between stages.** `clash_service.copy_clash_rules` bulk-
  copies all rules from a source `(estate_id, stage_id)` to a
  target `(estate_id, stage_id)` via upsert. This supports the
  common workflow of seeding a new stage release with the previous
  stage's restrictions.
- **Deletion is unilateral.** Deleting a rule does NOT automatically
  remove the lot from reciprocal rules. Admins must manage removal
  explicitly. This prevents cascading deletions from silently
  relaxing restrictions that may still be intentional.

## Consequences

### Positive

- **Symmetry is guaranteed.** Every clash constraint is enforced in
  both directions with no manual duplication.
- **Upsert prevents duplicates.** Creating the same rule twice is
  idempotent — the `cannot_match` lists merge.
- **Stage-copy accelerates onboarding.** When a developer releases a
  new stage with the same lot layout, an admin copies all clash
  rules from the previous stage in a single API call.
- **Simple mental model.** One rule = two-way restriction. Admins do
  not need to think about directionality.

### Negative

- **Deletion asymmetry may confuse admins.** Deleting a rule for Lot
  A does not remove Lot A from Lot B's `cannot_match`. This is
  deliberate (safety-first), but admins must remember to clean up
  both sides if they want to fully remove a constraint.
- **Write amplification.** Creating a rule with N entries in
  `cannot_match` may upsert up to N reciprocal rules. Acceptable at
  PoC scale (~50 rules per stage); revisit if rule counts grow into
  the thousands.
- **Copy does not invoke bidirectional sync.** Bulk copy uses a
  direct upsert path. If the target stage already has partial rules,
  reciprocal links may be incomplete. Acceptable because copy is
  expected to run on a fresh target stage.

### Follow-Ups

- Consider cascading reciprocal deletion behind an explicit
  `force_symmetric_delete=true` flag if admins request it.
- Add a "rule health check" endpoint that scans for asymmetric rules
  (rule A references B, but B does not reference A) and reports
  them.

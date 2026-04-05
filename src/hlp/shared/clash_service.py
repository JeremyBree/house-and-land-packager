"""Clash rule service: bidirectional enforcement, copy, and validation helpers."""

from __future__ import annotations

from sqlalchemy.orm import Session

from hlp.models.clash_rule import ClashRule
from hlp.repositories import clash_rule_repository


def _dedup(items: list[str]) -> list[str]:
    return list(dict.fromkeys(items))


def create_clash_rule(
    db: Session,
    estate_id: int,
    stage_id: int,
    lot_number: str,
    cannot_match: list[str],
) -> ClashRule:
    """Create or upsert a clash rule and ensure bidirectional reciprocal rules.

    For each lot in ``cannot_match``, ensure that lot has ``lot_number`` in ITS
    cannot_match list (upsert reciprocal).
    """
    cannot_match = _dedup([str(x) for x in cannot_match if str(x) != lot_number])

    existing = clash_rule_repository.get_by_scope(db, estate_id, stage_id, lot_number)
    if existing is None:
        rule = clash_rule_repository.create(
            db,
            estate_id=estate_id,
            stage_id=stage_id,
            lot_number=lot_number,
            cannot_match=cannot_match,
        )
    else:
        merged = _dedup([*existing.cannot_match, *cannot_match])
        existing.cannot_match = merged
        db.flush()
        rule = existing

    # Reciprocal: for each cannot_match entry, ensure reciprocal rule exists
    for other_lot in cannot_match:
        reciprocal = clash_rule_repository.get_by_scope(
            db, estate_id, stage_id, other_lot
        )
        if reciprocal is None:
            clash_rule_repository.create(
                db,
                estate_id=estate_id,
                stage_id=stage_id,
                lot_number=other_lot,
                cannot_match=[lot_number],
            )
        else:
            if lot_number not in reciprocal.cannot_match:
                reciprocal.cannot_match = _dedup(
                    [*reciprocal.cannot_match, lot_number]
                )
                db.flush()

    db.flush()
    return rule


def update_clash_rule(
    db: Session, rule_id: int, cannot_match: list[str]
) -> ClashRule:
    """Update cannot_match list and keep reciprocal links in sync.

    Adds reciprocal entries for new lots. Does NOT remove reciprocal entries when
    lots are removed from cannot_match (admins should manage removal explicitly).
    """
    rule = clash_rule_repository.get(db, rule_id)
    if rule is None:
        from hlp.shared.exceptions import ClashRuleNotFoundError

        raise ClashRuleNotFoundError(f"Clash rule {rule_id} not found")
    new_list = _dedup([str(x) for x in cannot_match if str(x) != rule.lot_number])
    rule.cannot_match = new_list
    db.flush()
    # Ensure reciprocal
    for other_lot in new_list:
        reciprocal = clash_rule_repository.get_by_scope(
            db, rule.estate_id, rule.stage_id, other_lot
        )
        if reciprocal is None:
            clash_rule_repository.create(
                db,
                estate_id=rule.estate_id,
                stage_id=rule.stage_id,
                lot_number=other_lot,
                cannot_match=[rule.lot_number],
            )
        elif rule.lot_number not in reciprocal.cannot_match:
            reciprocal.cannot_match = _dedup(
                [*reciprocal.cannot_match, rule.lot_number]
            )
    db.flush()
    return rule


def copy_clash_rules(
    db: Session,
    source_estate_id: int,
    source_stage_id: int,
    target_estate_id: int,
    target_stage_id: int,
) -> int:
    """Copy all clash rules from a source stage to a target stage (upsert)."""
    source_rules = clash_rule_repository.list_by_stage(
        db, source_estate_id, source_stage_id
    )
    if not source_rules:
        return 0
    payload = [
        {
            "estate_id": target_estate_id,
            "stage_id": target_stage_id,
            "lot_number": r.lot_number,
            "cannot_match": list(r.cannot_match),
        }
        for r in source_rules
    ]
    return clash_rule_repository.upsert_bulk(db, payload)


def get_restricted_lots_for(
    db: Session, estate_id: int, stage_id: int, lot_number: str
) -> list[str]:
    """Return the cannot_match list for a given lot scope (empty if no rule)."""
    rule = clash_rule_repository.get_by_scope(db, estate_id, stage_id, lot_number)
    if rule is None:
        return []
    return list(rule.cannot_match)


def validate_clash_submission(
    db: Session,
    estate_id: int,
    stage_id: int,
    submissions: list[dict],
) -> list[dict]:
    """Validate within-submission conflicts against clash rules.

    Each submission is ``{lot_number, design, facade}``. Returns a list of
    ``{lot_numbers: [a, b], design, facade, rule_id}`` violation dicts.
    """
    violations: list[dict] = []
    # Build lot -> submission index
    by_lot: dict[str, dict] = {}
    for sub in submissions:
        lot = str(sub.get("lot_number"))
        by_lot[lot] = sub

    seen_pairs: set[tuple[str, str]] = set()
    rules = clash_rule_repository.list_by_stage(db, estate_id, stage_id)
    for rule in rules:
        if rule.lot_number not in by_lot:
            continue
        a = by_lot[rule.lot_number]
        a_design = str(a.get("design", "")).strip().lower()
        a_facade = str(a.get("facade", "")).strip().lower()
        if not a_design or not a_facade:
            continue
        for other_lot in rule.cannot_match:
            if other_lot not in by_lot:
                continue
            b = by_lot[other_lot]
            b_design = str(b.get("design", "")).strip().lower()
            b_facade = str(b.get("facade", "")).strip().lower()
            if a_design == b_design and a_facade == b_facade:
                pair = tuple(sorted([rule.lot_number, other_lot]))
                if pair in seen_pairs:
                    continue
                seen_pairs.add(pair)
                violations.append(
                    {
                        "lot_numbers": list(pair),
                        "design": a.get("design"),
                        "facade": a.get("facade"),
                        "rule_id": rule.rule_id,
                    }
                )
    return violations

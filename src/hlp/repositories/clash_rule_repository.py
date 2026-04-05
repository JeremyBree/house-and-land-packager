"""ClashRule data access."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from hlp.models.clash_rule import ClashRule


def list_by_stage(db: Session, estate_id: int, stage_id: int) -> list[ClashRule]:
    stmt = (
        select(ClashRule)
        .where(ClashRule.estate_id == estate_id, ClashRule.stage_id == stage_id)
        .order_by(ClashRule.lot_number)
    )
    return list(db.execute(stmt).scalars().all())


def list_by_estate(db: Session, estate_id: int) -> list[ClashRule]:
    stmt = (
        select(ClashRule)
        .where(ClashRule.estate_id == estate_id)
        .order_by(ClashRule.stage_id, ClashRule.lot_number)
    )
    return list(db.execute(stmt).scalars().all())


def list_all(db: Session) -> list[ClashRule]:
    stmt = select(ClashRule).order_by(
        ClashRule.estate_id, ClashRule.stage_id, ClashRule.lot_number
    )
    return list(db.execute(stmt).scalars().all())


def get(db: Session, rule_id: int) -> ClashRule | None:
    return db.get(ClashRule, rule_id)


def get_by_scope(
    db: Session, estate_id: int, stage_id: int, lot_number: str
) -> ClashRule | None:
    stmt = select(ClashRule).where(
        ClashRule.estate_id == estate_id,
        ClashRule.stage_id == stage_id,
        ClashRule.lot_number == lot_number,
    )
    return db.execute(stmt).scalar_one_or_none()


def create(db: Session, **fields) -> ClashRule:
    rule = ClashRule(**fields)
    db.add(rule)
    db.flush()
    return rule


def update(db: Session, rule_id: int, cannot_match: list[str]) -> ClashRule:
    rule = get(db, rule_id)
    if rule is None:
        from hlp.shared.exceptions import ClashRuleNotFoundError

        raise ClashRuleNotFoundError(f"Clash rule {rule_id} not found")
    rule.cannot_match = list(cannot_match)
    db.flush()
    return rule


def delete(db: Session, rule_id: int) -> None:
    rule = get(db, rule_id)
    if rule is None:
        from hlp.shared.exceptions import ClashRuleNotFoundError

        raise ClashRuleNotFoundError(f"Clash rule {rule_id} not found")
    db.delete(rule)
    db.flush()


def upsert_bulk(db: Session, rules: list[dict]) -> int:
    """Insert or update rules by (estate_id, stage_id, lot_number). Returns count upserted."""
    count = 0
    for r in rules:
        estate_id = r["estate_id"]
        stage_id = r["stage_id"]
        lot_number = r["lot_number"]
        cannot_match = list(r.get("cannot_match", []))
        existing = get_by_scope(db, estate_id, stage_id, lot_number)
        if existing is None:
            create(
                db,
                estate_id=estate_id,
                stage_id=stage_id,
                lot_number=lot_number,
                cannot_match=cannot_match,
            )
        else:
            # Merge cannot_match lists (dedup)
            merged = list(dict.fromkeys([*existing.cannot_match, *cannot_match]))
            existing.cannot_match = merged
        count += 1
    db.flush()
    return count

"""Conflict detection service: scans clash rules vs house packages."""

from __future__ import annotations

from collections import defaultdict

from sqlalchemy import select
from sqlalchemy.orm import Session

from hlp.models.estate import Estate
from hlp.repositories import (
    clash_rule_repository,
    house_package_repository,
)


def _norm(value: str | None) -> str:
    return (value or "").strip().lower()


def _package_to_dict(pkg) -> dict:
    return {
        "package_id": pkg.package_id,
        "estate_id": pkg.estate_id,
        "stage_id": pkg.stage_id,
        "lot_number": pkg.lot_number,
        "design": pkg.design,
        "facade": pkg.facade,
        "colour_scheme": pkg.colour_scheme,
        "brand": pkg.brand,
        "source": pkg.source,
        "status": pkg.status,
        "flyer_path": pkg.flyer_path,
        "created_at": pkg.created_at,
        "updated_at": pkg.updated_at,
    }


def detect_all_conflicts(db: Session, estate_id: int | None = None) -> list[dict]:
    """Scan clash rules and packages; return conflict descriptors."""
    if estate_id is not None:
        rules = clash_rule_repository.list_by_estate(db, estate_id)
    else:
        rules = clash_rule_repository.list_all(db)

    conflicts: list[dict] = []
    seen_pairs: set[tuple[int, int]] = set()

    # Cache packages by (estate_id, stage_id, lot_number)
    pkg_cache: dict[tuple[int, int, str], list] = {}

    def _get_packages(e_id: int, s_id: int, lot: str):
        key = (e_id, s_id, lot)
        if key not in pkg_cache:
            pkg_cache[key] = house_package_repository.list_by_lot(db, e_id, s_id, lot)
        return pkg_cache[key]

    for rule in rules:
        a_packages = _get_packages(rule.estate_id, rule.stage_id, rule.lot_number)
        if not a_packages:
            continue
        for other_lot in rule.cannot_match:
            b_packages = _get_packages(rule.estate_id, rule.stage_id, other_lot)
            if not b_packages:
                continue
            for pa in a_packages:
                for pb in b_packages:
                    if pa.package_id == pb.package_id:
                        continue
                    if _norm(pa.design) != _norm(pb.design):
                        continue
                    if _norm(pa.facade) != _norm(pb.facade):
                        continue
                    pair = tuple(sorted([pa.package_id, pb.package_id]))
                    if pair in seen_pairs:
                        continue
                    seen_pairs.add(pair)

                    # Determine severity
                    colour_match = (
                        _norm(pa.colour_scheme) == _norm(pb.colour_scheme)
                        and _norm(pa.colour_scheme) != ""
                    )
                    if colour_match:
                        conflict_type = "design-facade-colour"
                        severity = "critical"
                    else:
                        conflict_type = "design-facade"
                        severity = "high"

                    # Order packages by package_id for stable output
                    if pa.package_id > pb.package_id:
                        pa, pb = pb, pa

                    conflicts.append(
                        {
                            "conflict_type": conflict_type,
                            "severity": severity,
                            "package_a": _package_to_dict(pa),
                            "package_b": _package_to_dict(pb),
                            "rule_id": rule.rule_id,
                            "estate_id": rule.estate_id,
                            "stage_id": rule.stage_id,
                            "lot_numbers": sorted([pa.lot_number, pb.lot_number]),
                        }
                    )
    return conflicts


def get_conflict_summary(db: Session) -> dict:
    """Return summary stats on all conflicts."""
    conflicts = detect_all_conflicts(db)
    total = len(conflicts)
    by_type: dict[str, int] = defaultdict(int)
    by_estate_count: dict[int, int] = defaultdict(int)
    for c in conflicts:
        by_type[c["conflict_type"]] += 1
        by_estate_count[c["estate_id"]] += 1

    # Load estate names
    estate_ids = list(by_estate_count.keys())
    estates_by_id: dict[int, str] = {}
    if estate_ids:
        stmt = select(Estate).where(Estate.estate_id.in_(estate_ids))
        for e in db.execute(stmt).scalars().all():
            estates_by_id[e.estate_id] = e.estate_name

    by_estate = [
        {
            "estate_id": eid,
            "estate_name": estates_by_id.get(eid, f"Estate {eid}"),
            "count": count,
        }
        for eid, count in sorted(
            by_estate_count.items(), key=lambda kv: (-kv[1], kv[0])
        )
    ]
    return {
        "total_conflicts": total,
        "by_type": dict(by_type),
        "by_estate": by_estate,
    }

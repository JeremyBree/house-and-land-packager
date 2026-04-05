"""Unit tests for hlp.shared.clash_service (uses in-memory SQLite via conftest)."""
from __future__ import annotations

from hlp.models.clash_rule import ClashRule
from hlp.models.developer import Developer
from hlp.models.enums import LotStatus, Source
from hlp.models.estate import Estate
from hlp.models.estate_stage import EstateStage
from hlp.models.region import Region
from hlp.models.stage_lot import StageLot
from hlp.shared import clash_service


def _seed_estate_stage(db):
    """Seed a region, developer, estate, and stage. Returns (estate_id, stage_id)."""
    region = Region(name="TestRegion")
    db.add(region)
    db.flush()
    dev = Developer(developer_name="TestDev")
    db.add(dev)
    db.flush()
    estate = Estate(
        developer_id=dev.developer_id,
        region_id=region.region_id,
        estate_name="TestEstate",
        suburb="TestSuburb",
        postcode="3000",
        active=True,
    )
    db.add(estate)
    db.flush()
    stage = EstateStage(estate_id=estate.estate_id, name="Stage 1")
    db.add(stage)
    db.flush()
    return estate.estate_id, stage.stage_id


def _seed_lots(db, stage_id, lot_numbers):
    """Seed lots with given lot numbers. Returns list of StageLot."""
    lots = []
    for ln in lot_numbers:
        lot = StageLot(
            stage_id=stage_id,
            lot_number=ln,
            status=LotStatus.AVAILABLE,
            source=Source.MANUAL,
        )
        db.add(lot)
        lots.append(lot)
    db.flush()
    return lots


# ---------------------------------------------------------------------------
# validate_clash_submission tests
# ---------------------------------------------------------------------------


def test_validate_clash_no_violations_returns_empty(db_session):
    estate_id, stage_id = _seed_estate_stage(db_session)
    # Create a clash rule: lot A1 cannot match A2
    clash_service.create_clash_rule(
        db_session, estate_id, stage_id, "A1", ["A2"]
    )
    db_session.flush()

    # Submit different designs on each lot — no violation
    submissions = [
        {"lot_number": "A1", "design": "Alpine", "facade": "Traditional"},
        {"lot_number": "A2", "design": "Baxter", "facade": "Modern"},
    ]
    violations = clash_service.validate_clash_submission(
        db_session, estate_id, stage_id, submissions
    )
    assert violations == []


def test_validate_clash_same_design_facade_on_restricted_lots_returns_violation(
    db_session,
):
    estate_id, stage_id = _seed_estate_stage(db_session)
    clash_service.create_clash_rule(
        db_session, estate_id, stage_id, "A1", ["A2"]
    )
    db_session.flush()

    submissions = [
        {"lot_number": "A1", "design": "Alpine", "facade": "Traditional"},
        {"lot_number": "A2", "design": "Alpine", "facade": "Traditional"},
    ]
    violations = clash_service.validate_clash_submission(
        db_session, estate_id, stage_id, submissions
    )
    assert len(violations) == 1
    v = violations[0]
    assert sorted(v["lot_numbers"]) == ["A1", "A2"]
    assert v["design"] == "Alpine"
    assert v["facade"] == "Traditional"


def test_validate_clash_different_design_no_violation(db_session):
    estate_id, stage_id = _seed_estate_stage(db_session)
    clash_service.create_clash_rule(
        db_session, estate_id, stage_id, "A1", ["A2"]
    )
    db_session.flush()

    submissions = [
        {"lot_number": "A1", "design": "Alpine", "facade": "Traditional"},
        {"lot_number": "A2", "design": "Baxter", "facade": "Traditional"},
    ]
    violations = clash_service.validate_clash_submission(
        db_session, estate_id, stage_id, submissions
    )
    assert violations == []


def test_validate_clash_case_insensitive_matching(db_session):
    estate_id, stage_id = _seed_estate_stage(db_session)
    clash_service.create_clash_rule(
        db_session, estate_id, stage_id, "A1", ["A2"]
    )
    db_session.flush()

    submissions = [
        {"lot_number": "A1", "design": "alpine", "facade": "TRADITIONAL"},
        {"lot_number": "A2", "design": "ALPINE", "facade": "traditional"},
    ]
    violations = clash_service.validate_clash_submission(
        db_session, estate_id, stage_id, submissions
    )
    assert len(violations) == 1


def test_validate_clash_multiple_violations_returned(db_session):
    estate_id, stage_id = _seed_estate_stage(db_session)
    # A1 cannot match A2 or A3
    clash_service.create_clash_rule(
        db_session, estate_id, stage_id, "A1", ["A2", "A3"]
    )
    db_session.flush()

    submissions = [
        {"lot_number": "A1", "design": "Alpine", "facade": "Traditional"},
        {"lot_number": "A2", "design": "Alpine", "facade": "Traditional"},
        {"lot_number": "A3", "design": "Alpine", "facade": "Traditional"},
    ]
    violations = clash_service.validate_clash_submission(
        db_session, estate_id, stage_id, submissions
    )
    # A1-A2, A1-A3, and (because bidirectional) A2-A3 only if a rule exists
    # Since A2 reciprocally has A1 in cannot_match and A3 has A1, but A2 and A3
    # don't restrict each other, we get exactly 2 violations: (A1,A2) and (A1,A3)
    assert len(violations) == 2
    pairs = [tuple(sorted(v["lot_numbers"])) for v in violations]
    assert ("A1", "A2") in pairs
    assert ("A1", "A3") in pairs


# ---------------------------------------------------------------------------
# get_restricted_lots_for tests
# ---------------------------------------------------------------------------


def test_get_restricted_lots_returns_cannot_match_list(db_session):
    estate_id, stage_id = _seed_estate_stage(db_session)
    clash_service.create_clash_rule(
        db_session, estate_id, stage_id, "A1", ["A2", "A3"]
    )
    db_session.flush()

    result = clash_service.get_restricted_lots_for(
        db_session, estate_id, stage_id, "A1"
    )
    assert set(result) == {"A2", "A3"}


def test_get_restricted_lots_missing_rule_returns_empty(db_session):
    estate_id, stage_id = _seed_estate_stage(db_session)
    result = clash_service.get_restricted_lots_for(
        db_session, estate_id, stage_id, "X99"
    )
    assert result == []


# ---------------------------------------------------------------------------
# bidirectional rule creation
# ---------------------------------------------------------------------------


def test_bidirectional_rule_creation(db_session):
    """When A cannot-match B is created, B's cannot_match should include A."""
    estate_id, stage_id = _seed_estate_stage(db_session)
    clash_service.create_clash_rule(
        db_session, estate_id, stage_id, "A1", ["A2"]
    )
    db_session.flush()

    # Verify reciprocal: A2 should have A1 in its cannot_match
    restricted = clash_service.get_restricted_lots_for(
        db_session, estate_id, stage_id, "A2"
    )
    assert "A1" in restricted

    # And A1 should still have A2
    restricted_a1 = clash_service.get_restricted_lots_for(
        db_session, estate_id, stage_id, "A1"
    )
    assert "A2" in restricted_a1

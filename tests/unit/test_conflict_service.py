"""Unit tests for hlp.shared.conflict_service (uses in-memory SQLite via conftest)."""
from __future__ import annotations

from hlp.models.developer import Developer
from hlp.models.enums import LotStatus, Source
from hlp.models.estate import Estate
from hlp.models.estate_stage import EstateStage
from hlp.models.house_package import HousePackage
from hlp.models.region import Region
from hlp.models.stage_lot import StageLot
from hlp.shared import clash_service, conflict_service


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


def _add_package(db, estate_id, stage_id, lot_number, design, facade, brand="Hermitage", colour_scheme=None):
    pkg = HousePackage(
        estate_id=estate_id,
        stage_id=stage_id,
        lot_number=lot_number,
        design=design,
        facade=facade,
        brand=brand,
        colour_scheme=colour_scheme,
    )
    db.add(pkg)
    db.flush()
    return pkg


def test_no_conflicts_when_no_packages(db_session):
    estate_id, stage_id = _seed_estate_stage(db_session)
    clash_service.create_clash_rule(
        db_session, estate_id, stage_id, "A1", ["A2"]
    )
    db_session.flush()

    conflicts = conflict_service.detect_all_conflicts(db_session)
    assert conflicts == []


def test_detect_design_facade_conflict(db_session):
    estate_id, stage_id = _seed_estate_stage(db_session)
    clash_service.create_clash_rule(
        db_session, estate_id, stage_id, "A1", ["A2"]
    )
    db_session.flush()

    _add_package(db_session, estate_id, stage_id, "A1", "Alpine", "Traditional")
    _add_package(db_session, estate_id, stage_id, "A2", "Alpine", "Traditional")

    conflicts = conflict_service.detect_all_conflicts(db_session)
    assert len(conflicts) == 1
    c = conflicts[0]
    assert c["conflict_type"] == "design-facade"
    assert c["severity"] == "high"
    assert sorted(c["lot_numbers"]) == ["A1", "A2"]


def test_no_conflict_when_different_facade(db_session):
    estate_id, stage_id = _seed_estate_stage(db_session)
    clash_service.create_clash_rule(
        db_session, estate_id, stage_id, "A1", ["A2"]
    )
    db_session.flush()

    _add_package(db_session, estate_id, stage_id, "A1", "Alpine", "Traditional")
    _add_package(db_session, estate_id, stage_id, "A2", "Alpine", "Modern")

    conflicts = conflict_service.detect_all_conflicts(db_session)
    assert conflicts == []


def test_case_insensitive_design_facade_match(db_session):
    estate_id, stage_id = _seed_estate_stage(db_session)
    clash_service.create_clash_rule(
        db_session, estate_id, stage_id, "A1", ["A2"]
    )
    db_session.flush()

    _add_package(db_session, estate_id, stage_id, "A1", "alpine", "traditional")
    _add_package(db_session, estate_id, stage_id, "A2", "ALPINE", "TRADITIONAL")

    conflicts = conflict_service.detect_all_conflicts(db_session)
    assert len(conflicts) == 1


def test_colour_scheme_escalates_to_critical(db_session):
    estate_id, stage_id = _seed_estate_stage(db_session)
    clash_service.create_clash_rule(
        db_session, estate_id, stage_id, "A1", ["A2"]
    )
    db_session.flush()

    _add_package(
        db_session, estate_id, stage_id, "A1", "Alpine", "Traditional",
        colour_scheme="Coastal",
    )
    _add_package(
        db_session, estate_id, stage_id, "A2", "Alpine", "Traditional",
        colour_scheme="Coastal",
    )

    conflicts = conflict_service.detect_all_conflicts(db_session)
    assert len(conflicts) == 1
    c = conflicts[0]
    assert c["conflict_type"] == "design-facade-colour"
    assert c["severity"] == "critical"


def test_dedup_by_sorted_package_pair(db_session):
    """Bidirectional rules should not cause duplicate conflict entries."""
    estate_id, stage_id = _seed_estate_stage(db_session)
    # Create rule A1 cannot-match A2 (also creates reciprocal A2 cannot-match A1)
    clash_service.create_clash_rule(
        db_session, estate_id, stage_id, "A1", ["A2"]
    )
    db_session.flush()

    _add_package(db_session, estate_id, stage_id, "A1", "Alpine", "Traditional")
    _add_package(db_session, estate_id, stage_id, "A2", "Alpine", "Traditional")

    conflicts = conflict_service.detect_all_conflicts(db_session)
    # Should be exactly 1, not 2 (deduped by sorted package pair)
    assert len(conflicts) == 1

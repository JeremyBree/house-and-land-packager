"""Integration tests: /api/conflicts endpoints."""
from __future__ import annotations

from fastapi.testclient import TestClient


# ---- no conflicts ------------------------------------------------------------


def test_no_conflicts_returns_empty_list(
    client: TestClient, admin_headers, seeded_users
):
    r = client.get("/api/conflicts", headers=admin_headers)
    assert r.status_code == 200
    assert r.json() == []


# ---- conflict detection ------------------------------------------------------


def test_detect_conflict_when_same_design_facade_on_restricted_lots(
    client: TestClient, admin_headers, sample_stages_and_lots
):
    """Create a clash rule and two packages with same design/facade -> conflict."""
    data = sample_stages_and_lots
    eid = data["estate_id"]
    sid = data["stage_a_id"]

    # Create clash rule: A1 cannot match A2
    client.post(
        f"/api/estates/{eid}/stages/{sid}/clash-rules",
        json={
            "estate_id": eid,
            "stage_id": sid,
            "lot_number": "A1",
            "cannot_match": ["A2"],
        },
        headers=admin_headers,
    )

    # Create package on A1
    client.post(
        "/api/packages",
        json={
            "estate_id": eid,
            "stage_id": sid,
            "lot_number": "A1",
            "design": "Alpine",
            "facade": "Traditional",
            "brand": "Hermitage",
        },
        headers=admin_headers,
    )

    # Create package on A2 with same design/facade
    client.post(
        "/api/packages",
        json={
            "estate_id": eid,
            "stage_id": sid,
            "lot_number": "A2",
            "design": "Alpine",
            "facade": "Traditional",
            "brand": "Hermitage",
        },
        headers=admin_headers,
    )

    # Check conflicts
    r = client.get(f"/api/conflicts?estate_id={eid}", headers=admin_headers)
    assert r.status_code == 200
    conflicts = r.json()
    assert len(conflicts) >= 1
    c = conflicts[0]
    assert c["conflict_type"] == "design-facade"
    assert c["severity"] == "high"
    assert sorted(c["lot_numbers"]) == ["A1", "A2"]


def test_conflict_summary_includes_counts(
    client: TestClient, admin_headers, sample_stages_and_lots
):
    """Summary should show total_conflicts > 0 when conflicts exist."""
    data = sample_stages_and_lots
    eid = data["estate_id"]
    sid = data["stage_a_id"]

    # Create clash rule + conflicting packages
    client.post(
        f"/api/estates/{eid}/stages/{sid}/clash-rules",
        json={
            "estate_id": eid,
            "stage_id": sid,
            "lot_number": "A1",
            "cannot_match": ["A2"],
        },
        headers=admin_headers,
    )
    for lot in ("A1", "A2"):
        client.post(
            "/api/packages",
            json={
                "estate_id": eid,
                "stage_id": sid,
                "lot_number": lot,
                "design": "Alpine",
                "facade": "Traditional",
                "brand": "Hermitage",
            },
            headers=admin_headers,
        )

    r = client.get("/api/conflicts/summary", headers=admin_headers)
    assert r.status_code == 200
    body = r.json()
    assert body["total_conflicts"] >= 1
    assert "by_type" in body
    assert "by_estate" in body


def test_filter_conflicts_by_estate(
    client: TestClient, admin_headers, sample_stages_and_lots
):
    data = sample_stages_and_lots
    eid = data["estate_id"]
    sid = data["stage_a_id"]

    # Seed a clash + conflicting packages
    client.post(
        f"/api/estates/{eid}/stages/{sid}/clash-rules",
        json={
            "estate_id": eid,
            "stage_id": sid,
            "lot_number": "A1",
            "cannot_match": ["A2"],
        },
        headers=admin_headers,
    )
    for lot in ("A1", "A2"):
        client.post(
            "/api/packages",
            json={
                "estate_id": eid,
                "stage_id": sid,
                "lot_number": lot,
                "design": "Alpine",
                "facade": "Traditional",
                "brand": "Hermitage",
            },
            headers=admin_headers,
        )

    # Filter by estate_id
    r = client.get(f"/api/conflicts?estate_id={eid}", headers=admin_headers)
    assert r.status_code == 200
    assert len(r.json()) >= 1

    # Filter by non-existent estate should return empty
    r2 = client.get("/api/conflicts?estate_id=999999", headers=admin_headers)
    assert r2.status_code == 200
    assert r2.json() == []


def test_no_conflict_when_different_designs(
    client: TestClient, admin_headers, sample_stages_and_lots
):
    data = sample_stages_and_lots
    eid = data["estate_id"]
    sid = data["stage_a_id"]

    client.post(
        f"/api/estates/{eid}/stages/{sid}/clash-rules",
        json={
            "estate_id": eid,
            "stage_id": sid,
            "lot_number": "A1",
            "cannot_match": ["A2"],
        },
        headers=admin_headers,
    )
    client.post(
        "/api/packages",
        json={
            "estate_id": eid,
            "stage_id": sid,
            "lot_number": "A1",
            "design": "Alpine",
            "facade": "Traditional",
            "brand": "Hermitage",
        },
        headers=admin_headers,
    )
    client.post(
        "/api/packages",
        json={
            "estate_id": eid,
            "stage_id": sid,
            "lot_number": "A2",
            "design": "Baxter",
            "facade": "Modern",
            "brand": "Hermitage",
        },
        headers=admin_headers,
    )

    r = client.get(f"/api/conflicts?estate_id={eid}", headers=admin_headers)
    assert r.status_code == 200
    assert r.json() == []


def test_unauth_401(client: TestClient):
    r = client.get("/api/conflicts")
    assert r.status_code == 401

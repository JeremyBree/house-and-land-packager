"""Integration tests: /api/estates/{id}/stages and /api/stages/{id}."""
from __future__ import annotations

from fastapi.testclient import TestClient


# ---- list stages -----------------------------------------------------------


def test_list_stages_for_estate(
    client: TestClient, sales_headers, sample_stages_and_lots
):
    estate_id = sample_stages_and_lots["estate_id"]
    r = client.get(f"/api/estates/{estate_id}/stages", headers=sales_headers)
    assert r.status_code == 200
    body = r.json()
    assert isinstance(body, list)
    assert len(body) == 2
    names = sorted(s["name"] for s in body)
    assert names == ["Stage 1", "Stage 2"]


def test_list_stages_empty_estate(
    client: TestClient, admin_headers, sample_data
):
    # Use an estate that has no stages.
    estate_id = sample_data["estates"][1]["estate_id"]
    r = client.get(f"/api/estates/{estate_id}/stages", headers=admin_headers)
    assert r.status_code == 200
    assert r.json() == []


def test_list_stages_estate_not_found_404(
    client: TestClient, admin_headers, seeded_users
):
    r = client.get("/api/estates/999999/stages", headers=admin_headers)
    assert r.status_code == 404


# ---- create stage ----------------------------------------------------------


def test_admin_creates_stage_201(
    client: TestClient, admin_headers, sample_data
):
    estate_id = sample_data["estates"][0]["estate_id"]
    r = client.post(
        f"/api/estates/{estate_id}/stages",
        json={"name": "Stage Alpha", "lot_count": 30, "status": "Active"},
        headers=admin_headers,
    )
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["name"] == "Stage Alpha"
    assert body["estate_id"] == estate_id
    assert body["status"] == "Active"


def test_stage_create_payload_validation(
    client: TestClient, admin_headers, sample_data
):
    estate_id = sample_data["estates"][0]["estate_id"]
    r = client.post(
        f"/api/estates/{estate_id}/stages",
        json={"name": "Bad", "status": "Nonsense"},
        headers=admin_headers,
    )
    assert r.status_code == 422


def test_non_admin_create_stage_403(
    client: TestClient, sales_headers, sample_data
):
    estate_id = sample_data["estates"][0]["estate_id"]
    r = client.post(
        f"/api/estates/{estate_id}/stages",
        json={"name": "Denied"},
        headers=sales_headers,
    )
    assert r.status_code == 403


# ---- detail (with stats) ---------------------------------------------------


def test_get_stage_detail_returns_lot_count_and_status_breakdown(
    client: TestClient, sales_headers, sample_stages_and_lots
):
    stage_id = sample_stages_and_lots["stage_a_id"]
    r = client.get(f"/api/stages/{stage_id}", headers=sales_headers)
    assert r.status_code == 200
    body = r.json()
    assert body["stage_id"] == stage_id
    assert body["lot_count_actual"] == 5
    breakdown = body["status_breakdown"]
    assert breakdown.get("Available") == 2
    assert breakdown.get("Hold") == 1
    assert breakdown.get("Sold") == 1
    assert breakdown.get("Unavailable") == 1


def test_get_missing_stage_404(client: TestClient, sales_headers, seeded_users):
    r = client.get("/api/stages/999999", headers=sales_headers)
    assert r.status_code == 404


# ---- update ---------------------------------------------------------------


def test_admin_updates_stage(
    client: TestClient, admin_headers, sample_stages_and_lots
):
    stage_id = sample_stages_and_lots["stage_a_id"]
    r = client.patch(
        f"/api/stages/{stage_id}",
        json={"name": "Renamed Stage", "status": "Completed"},
        headers=admin_headers,
    )
    assert r.status_code == 200
    body = r.json()
    assert body["name"] == "Renamed Stage"
    assert body["status"] == "Completed"


# ---- delete (cascade) -----------------------------------------------------


def test_admin_deletes_stage_cascades_to_lots_204(
    client: TestClient, admin_headers, sales_headers, sample_stages_and_lots
):
    stage_id = sample_stages_and_lots["stage_a_id"]
    r = client.delete(f"/api/stages/{stage_id}", headers=admin_headers)
    assert r.status_code == 204

    # Lots under the deleted stage should no longer be listable (404 on stage).
    r2 = client.get(f"/api/stages/{stage_id}/lots", headers=sales_headers)
    assert r2.status_code == 404

    # A previously-seeded lot id no longer exists.
    any_lot_id = sample_stages_and_lots["stage_a_lot_ids"][0]
    r3 = client.get(f"/api/lots/{any_lot_id}", headers=sales_headers)
    assert r3.status_code == 404


def test_delete_nonexistent_stage_404(
    client: TestClient, admin_headers, seeded_users
):
    r = client.delete("/api/stages/999999", headers=admin_headers)
    assert r.status_code == 404

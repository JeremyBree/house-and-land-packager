"""Integration tests: /api/lots/{id}/status + /api/lots/{id}/status-history."""
from __future__ import annotations

from fastapi.testclient import TestClient


def _transition(client, lot_id, headers, new_status="Hold", reason="testing"):
    return client.post(
        f"/api/lots/{lot_id}/status",
        json={"new_status": new_status, "reason": reason},
        headers=headers,
    )


# ---- RBAC ------------------------------------------------------------------


def test_admin_transitions_lot_status(
    client: TestClient, admin_headers, sample_stages_and_lots
):
    lot_id = sample_stages_and_lots["stage_a_lot_ids"][0]  # Available
    r = _transition(client, lot_id, admin_headers, new_status="Hold")
    assert r.status_code == 200, r.text
    assert r.json()["status"] == "Hold"


def test_pricing_role_can_transition_status(
    client: TestClient, pricing_headers, sample_stages_and_lots
):
    lot_id = sample_stages_and_lots["stage_a_lot_ids"][1]
    r = _transition(client, lot_id, pricing_headers, new_status="Sold")
    assert r.status_code == 200, r.text
    assert r.json()["status"] == "Sold"


def test_sales_cannot_transition_status_403(
    client: TestClient, sales_headers, sample_stages_and_lots
):
    lot_id = sample_stages_and_lots["stage_a_lot_ids"][0]
    r = _transition(client, lot_id, sales_headers)
    assert r.status_code == 403


def test_requester_cannot_transition_status_403(
    client: TestClient, requester_headers, sample_stages_and_lots
):
    lot_id = sample_stages_and_lots["stage_a_lot_ids"][0]
    r = _transition(client, lot_id, requester_headers)
    assert r.status_code == 403


# ---- validation / not-found -----------------------------------------------


def test_transition_missing_lot_404(
    client: TestClient, admin_headers, seeded_users
):
    r = _transition(client, 999999, admin_headers)
    assert r.status_code == 404


def test_transition_body_validation(
    client: TestClient, admin_headers, sample_stages_and_lots
):
    lot_id = sample_stages_and_lots["stage_a_lot_ids"][0]
    r = client.post(
        f"/api/lots/{lot_id}/status",
        json={"new_status": "NotARealStatus", "reason": "x"},
        headers=admin_headers,
    )
    assert r.status_code == 422


# ---- side effects: last_confirmed_date, history ---------------------------


def test_transition_updates_last_confirmed_date(
    client: TestClient, admin_headers, sample_stages_and_lots
):
    lot_id = sample_stages_and_lots["stage_a_lot_ids"][0]
    r = _transition(client, lot_id, admin_headers, new_status="Hold")
    assert r.status_code == 200
    body = r.json()
    assert body["last_confirmed_date"] is not None


def test_transition_creates_status_history_entry(
    client: TestClient, admin_headers, sample_stages_and_lots
):
    lot_id = sample_stages_and_lots["stage_a_lot_ids"][0]
    _transition(client, lot_id, admin_headers, new_status="Hold", reason="first")

    r = client.get(f"/api/lots/{lot_id}/status-history", headers=admin_headers)
    assert r.status_code == 200
    entries = r.json()
    assert len(entries) == 1
    e = entries[0]
    assert e["lot_id"] == lot_id
    assert e["previous_status"] == "Available"
    assert e["new_status"] == "Hold"
    assert e["source_detail"] == "first"
    assert e["triggering_agent"].startswith("manual:")


def test_status_history_returns_entries_in_descending_order(
    client: TestClient, admin_headers, sample_stages_and_lots
):
    lot_id = sample_stages_and_lots["stage_a_lot_ids"][0]
    _transition(client, lot_id, admin_headers, new_status="Hold", reason="r1")
    _transition(client, lot_id, admin_headers, new_status="Sold", reason="r2")
    _transition(
        client, lot_id, admin_headers, new_status="Unavailable", reason="r3"
    )

    r = client.get(f"/api/lots/{lot_id}/status-history", headers=admin_headers)
    assert r.status_code == 200
    entries = r.json()
    assert len(entries) == 3
    # Most recent first
    assert entries[0]["new_status"] == "Unavailable"
    assert entries[1]["new_status"] == "Sold"
    assert entries[2]["new_status"] == "Hold"


def test_status_history_for_unknown_lot_404_or_empty(
    client: TestClient, admin_headers, seeded_users
):
    r = client.get("/api/lots/999999/status-history", headers=admin_headers)
    assert r.status_code in (404, 200)
    if r.status_code == 200:
        assert r.json() == []


def test_status_refresh_same_status_still_creates_history(
    client: TestClient, admin_headers, sample_stages_and_lots
):
    lot_id = sample_stages_and_lots["stage_a_lot_ids"][0]  # starts Available
    r = _transition(
        client, lot_id, admin_headers, new_status="Available", reason="refresh"
    )
    assert r.status_code == 200
    h = client.get(f"/api/lots/{lot_id}/status-history", headers=admin_headers)
    assert h.status_code == 200
    entries = h.json()
    assert len(entries) == 1
    assert entries[0]["previous_status"] == "Available"
    assert entries[0]["new_status"] == "Available"

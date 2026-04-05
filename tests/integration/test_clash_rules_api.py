"""Integration tests: /api/clash-rules, /api/estates/{id}/clash-rules, etc."""
from __future__ import annotations

from fastapi.testclient import TestClient


# ---- create ------------------------------------------------------------------


def test_admin_creates_clash_rule_201(
    client: TestClient, admin_headers, sample_stages_and_lots
):
    data = sample_stages_and_lots
    r = client.post(
        f"/api/estates/{data['estate_id']}/stages/{data['stage_a_id']}/clash-rules",
        json={
            "estate_id": data["estate_id"],
            "stage_id": data["stage_a_id"],
            "lot_number": "A1",
            "cannot_match": ["A2"],
        },
        headers=admin_headers,
    )
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["lot_number"] == "A1"
    assert "A2" in body["cannot_match"]

    # Verify bidirectional reciprocal was created
    r2 = client.get(
        f"/api/stages/{data['stage_a_id']}/clash-rules",
        headers=admin_headers,
    )
    assert r2.status_code == 200
    rules = r2.json()
    a2_rule = next((r for r in rules if r["lot_number"] == "A2"), None)
    assert a2_rule is not None
    assert "A1" in a2_rule["cannot_match"]


def test_non_admin_create_403(
    client: TestClient, sales_headers, sample_stages_and_lots
):
    data = sample_stages_and_lots
    r = client.post(
        f"/api/estates/{data['estate_id']}/stages/{data['stage_a_id']}/clash-rules",
        json={
            "estate_id": data["estate_id"],
            "stage_id": data["stage_a_id"],
            "lot_number": "A1",
            "cannot_match": ["A2"],
        },
        headers=sales_headers,
    )
    assert r.status_code == 403


def test_unauth_401(client: TestClient, sample_stages_and_lots):
    data = sample_stages_and_lots
    r = client.get(f"/api/estates/{data['estate_id']}/clash-rules")
    assert r.status_code == 401


# ---- list --------------------------------------------------------------------


def test_list_clash_rules_by_estate(
    client: TestClient, admin_headers, sample_clash_rules
):
    eid = sample_clash_rules["estate_id"]
    r = client.get(f"/api/estates/{eid}/clash-rules", headers=admin_headers)
    assert r.status_code == 200
    rules = r.json()
    assert len(rules) == 3
    lot_numbers = {rule["lot_number"] for rule in rules}
    assert lot_numbers == {"A1", "A2", "A3"}


def test_list_clash_rules_by_stage(
    client: TestClient, admin_headers, sample_clash_rules
):
    sid = sample_clash_rules["stage_id"]
    r = client.get(f"/api/stages/{sid}/clash-rules", headers=admin_headers)
    assert r.status_code == 200
    rules = r.json()
    assert len(rules) == 3


# ---- get by id ---------------------------------------------------------------


def test_get_clash_rule_by_id(
    client: TestClient, admin_headers, sample_clash_rules
):
    rule_id = sample_clash_rules["rule_ids"][0]
    r = client.get(f"/api/clash-rules/{rule_id}", headers=admin_headers)
    assert r.status_code == 200
    body = r.json()
    assert body["rule_id"] == rule_id
    assert body["lot_number"] == "A1"


def test_get_missing_rule_404(client: TestClient, admin_headers, seeded_users):
    r = client.get("/api/clash-rules/999999", headers=admin_headers)
    assert r.status_code == 404


# ---- update ------------------------------------------------------------------


def test_update_clash_rule_updates_cannot_match(
    client: TestClient, admin_headers, sample_clash_rules
):
    rule_id = sample_clash_rules["rule_ids"][0]
    r = client.patch(
        f"/api/clash-rules/{rule_id}",
        json={"cannot_match": ["A2", "A3", "A4"]},
        headers=admin_headers,
    )
    assert r.status_code == 200
    body = r.json()
    assert set(body["cannot_match"]) == {"A2", "A3", "A4"}


# ---- delete ------------------------------------------------------------------


def test_delete_clash_rule_204(
    client: TestClient, admin_headers, sample_clash_rules
):
    rule_id = sample_clash_rules["rule_ids"][0]
    r = client.delete(f"/api/clash-rules/{rule_id}", headers=admin_headers)
    assert r.status_code == 204

    # Confirm it's gone
    r2 = client.get(f"/api/clash-rules/{rule_id}", headers=admin_headers)
    assert r2.status_code == 404


def test_non_admin_delete_403(
    client: TestClient, sales_headers, sample_clash_rules
):
    rule_id = sample_clash_rules["rule_ids"][0]
    r = client.delete(f"/api/clash-rules/{rule_id}", headers=sales_headers)
    assert r.status_code == 403


# ---- duplicate scope ---------------------------------------------------------


def test_duplicate_scope_returns_409_or_upserts(
    client: TestClient, admin_headers, sample_stages_and_lots
):
    """Creating a clash rule for an already-existing scope should upsert
    (merge cannot_match) rather than error, per service layer design."""
    data = sample_stages_and_lots
    payload = {
        "estate_id": data["estate_id"],
        "stage_id": data["stage_a_id"],
        "lot_number": "A1",
        "cannot_match": ["A2"],
    }
    url = f"/api/estates/{data['estate_id']}/stages/{data['stage_a_id']}/clash-rules"
    r1 = client.post(url, json=payload, headers=admin_headers)
    assert r1.status_code == 201

    # Post again with additional cannot_match
    payload2 = {**payload, "cannot_match": ["A3"]}
    r2 = client.post(url, json=payload2, headers=admin_headers)
    # Service upserts (merges) — should return 201 with merged list
    assert r2.status_code == 201
    body = r2.json()
    assert "A2" in body["cannot_match"]
    assert "A3" in body["cannot_match"]


# ---- copy --------------------------------------------------------------------


def test_copy_clash_rules_between_stages(
    client: TestClient, admin_headers, sample_clash_rules, sample_stages_and_lots
):
    source_stage_id = sample_clash_rules["stage_id"]
    target_stage_id = sample_stages_and_lots["stage_b_id"]
    target_estate_id = sample_clash_rules["estate_id"]

    r = client.post(
        f"/api/stages/{source_stage_id}/clash-rules/copy",
        json={
            "target_estate_id": target_estate_id,
            "target_stage_id": target_stage_id,
        },
        headers=admin_headers,
    )
    assert r.status_code == 200
    body = r.json()
    assert body["copied"] == 3

    # Verify rules exist on target stage
    r2 = client.get(
        f"/api/stages/{target_stage_id}/clash-rules",
        headers=admin_headers,
    )
    assert r2.status_code == 200
    assert len(r2.json()) == 3


def test_copy_clash_rules_upsert_dedup(
    client: TestClient, admin_headers, sample_clash_rules, sample_stages_and_lots
):
    """Copying twice should not double entries (upsert behaviour)."""
    source_stage_id = sample_clash_rules["stage_id"]
    target_stage_id = sample_stages_and_lots["stage_b_id"]
    target_estate_id = sample_clash_rules["estate_id"]

    copy_payload = {
        "target_estate_id": target_estate_id,
        "target_stage_id": target_stage_id,
    }
    url = f"/api/stages/{source_stage_id}/clash-rules/copy"
    client.post(url, json=copy_payload, headers=admin_headers)
    client.post(url, json=copy_payload, headers=admin_headers)

    r = client.get(
        f"/api/stages/{target_stage_id}/clash-rules",
        headers=admin_headers,
    )
    assert r.status_code == 200
    rules = r.json()
    # Still exactly 3, not 6
    assert len(rules) == 3


def test_copy_clash_rules_to_different_estate(
    client: TestClient, admin_headers, sample_clash_rules, sample_data
):
    """Copy rules to a stage under a different estate."""
    source_stage_id = sample_clash_rules["stage_id"]

    # Create a stage under the second estate
    second_estate_id = sample_data["estates"][1]["estate_id"]
    r_stage = client.post(
        f"/api/estates/{second_estate_id}/stages",
        json={"name": "Cross-Estate Stage"},
        headers=admin_headers,
    )
    assert r_stage.status_code == 201
    target_stage_id = r_stage.json()["stage_id"]

    r = client.post(
        f"/api/stages/{source_stage_id}/clash-rules/copy",
        json={
            "target_estate_id": second_estate_id,
            "target_stage_id": target_stage_id,
        },
        headers=admin_headers,
    )
    assert r.status_code == 200
    assert r.json()["copied"] == 3


# ---- bidirectional enforcement -----------------------------------------------


def test_bidirectional_enforcement_verified(
    client: TestClient, admin_headers, sample_stages_and_lots
):
    """Create rule for lot A1 -> [A2], verify A2's rules include A1."""
    data = sample_stages_and_lots
    # Create rule: A1 cannot match A2
    client.post(
        f"/api/estates/{data['estate_id']}/stages/{data['stage_a_id']}/clash-rules",
        json={
            "estate_id": data["estate_id"],
            "stage_id": data["stage_a_id"],
            "lot_number": "A1",
            "cannot_match": ["A2"],
        },
        headers=admin_headers,
    )

    # List rules for the stage and find A2's rule
    r = client.get(
        f"/api/stages/{data['stage_a_id']}/clash-rules",
        headers=admin_headers,
    )
    assert r.status_code == 200
    rules = r.json()
    a2_rule = next((rule for rule in rules if rule["lot_number"] == "A2"), None)
    assert a2_rule is not None
    assert "A1" in a2_rule["cannot_match"]

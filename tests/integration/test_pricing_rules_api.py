"""Integration tests: /api/pricing-rule-categories and /api/pricing-rules endpoints."""
from __future__ import annotations

from fastapi.testclient import TestClient


BRAND = "Hermitage Homes"


# =============================================================================
# Category tests
# =============================================================================


def test_list_categories(client: TestClient, admin_headers, seeded_users):
    r = client.get(
        "/api/pricing-rule-categories",
        params={"brand": BRAND},
        headers=admin_headers,
    )
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_create_category(client: TestClient, admin_headers, seeded_users):
    r = client.post(
        "/api/pricing-rule-categories",
        json={"name": "Base Extras", "brand": BRAND, "sort_order": 1},
        headers=admin_headers,
    )
    assert r.status_code == 201
    body = r.json()
    assert body["name"] == "Base Extras"
    assert body["brand"] == BRAND


def test_update_category(client: TestClient, admin_headers, seeded_users):
    r_create = client.post(
        "/api/pricing-rule-categories",
        json={"name": "OldName", "brand": BRAND, "sort_order": 0},
        headers=admin_headers,
    )
    cat_id = r_create.json()["category_id"]

    r = client.patch(
        f"/api/pricing-rule-categories/{cat_id}",
        json={"name": "NewName"},
        headers=admin_headers,
    )
    assert r.status_code == 200
    assert r.json()["name"] == "NewName"


def test_delete_category(client: TestClient, admin_headers, seeded_users):
    r_create = client.post(
        "/api/pricing-rule-categories",
        json={"name": "Temporary", "brand": BRAND, "sort_order": 99},
        headers=admin_headers,
    )
    cat_id = r_create.json()["category_id"]

    r = client.delete(
        f"/api/pricing-rule-categories/{cat_id}",
        headers=admin_headers,
    )
    assert r.status_code == 204


def test_non_admin_category_403(client: TestClient, sales_headers, seeded_users):
    r = client.post(
        "/api/pricing-rule-categories",
        json={"name": "Test", "brand": BRAND, "sort_order": 0},
        headers=sales_headers,
    )
    assert r.status_code == 403


# =============================================================================
# Global rules tests
# =============================================================================


def _create_global_rule(client, headers, **overrides):
    """Helper to create a global pricing rule."""
    payload = {
        "brand": BRAND,
        "item_name": "Test Item",
        "cost": "100.00",
        "cell_row": 5,
        "cell_col": 3,
        "cost_cell_row": 5,
        "cost_cell_col": 4,
        "sort_order": 0,
    }
    payload.update(overrides)
    return client.post(
        "/api/pricing-rules/global",
        json=payload,
        headers=headers,
    )


def test_list_global_rules_by_brand(client: TestClient, admin_headers, seeded_users):
    _create_global_rule(client, admin_headers, item_name="Alpha")
    _create_global_rule(client, admin_headers, item_name="Beta")

    r = client.get(
        "/api/pricing-rules/global",
        params={"brand": BRAND},
        headers=admin_headers,
    )
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 2
    names = {i["item_name"] for i in items}
    assert "Alpha" in names
    assert "Beta" in names


def test_create_global_rule(client: TestClient, admin_headers, seeded_users):
    r = _create_global_rule(client, admin_headers, item_name="Corner Uplift")
    assert r.status_code == 201
    body = r.json()
    assert body["item_name"] == "Corner Uplift"
    assert body["brand"] == BRAND


def test_get_global_rule(client: TestClient, admin_headers, seeded_users):
    r_create = _create_global_rule(client, admin_headers)
    rule_id = r_create.json()["rule_id"]

    r = client.get(f"/api/pricing-rules/global/{rule_id}", headers=admin_headers)
    assert r.status_code == 200
    assert r.json()["rule_id"] == rule_id


def test_update_global_rule(client: TestClient, admin_headers, seeded_users):
    r_create = _create_global_rule(client, admin_headers, item_name="Old")
    rule_id = r_create.json()["rule_id"]

    r = client.patch(
        f"/api/pricing-rules/global/{rule_id}",
        json={"item_name": "Updated"},
        headers=admin_headers,
    )
    assert r.status_code == 200
    assert r.json()["item_name"] == "Updated"


def test_delete_global_rule(client: TestClient, admin_headers, seeded_users):
    r_create = _create_global_rule(client, admin_headers)
    rule_id = r_create.json()["rule_id"]

    r = client.delete(f"/api/pricing-rules/global/{rule_id}", headers=admin_headers)
    assert r.status_code == 204

    r2 = client.get(f"/api/pricing-rules/global/{rule_id}", headers=admin_headers)
    assert r2.status_code == 404


def test_duplicate_global_rule_creates_copy(client: TestClient, admin_headers, seeded_users):
    r_create = _create_global_rule(
        client, admin_headers, item_name="Original", cost="250.00"
    )
    rule_id = r_create.json()["rule_id"]

    r = client.post(
        f"/api/pricing-rules/global/{rule_id}/duplicate",
        headers=admin_headers,
    )
    assert r.status_code == 201
    dup = r.json()
    assert dup["rule_id"] != rule_id
    assert dup["item_name"] == "Original"
    assert float(dup["cost"]) == 250.00


# =============================================================================
# Stage rules tests
# =============================================================================


def _create_stage_rule(client, headers, estate_id, stage_id, **overrides):
    payload = {
        "brand": BRAND,
        "estate_id": estate_id,
        "stage_id": stage_id,
        "item_name": "Stage Item",
        "cost": "75.00",
        "cell_row": 10,
        "cell_col": 2,
        "cost_cell_row": 10,
        "cost_cell_col": 3,
        "sort_order": 0,
    }
    payload.update(overrides)
    return client.post(
        "/api/pricing-rules/stage",
        json=payload,
        headers=headers,
    )


def test_list_stage_rules_by_estate_stage(
    client: TestClient, admin_headers, sample_stages_and_lots
):
    eid = sample_stages_and_lots["estate_id"]
    sid = sample_stages_and_lots["stage_a_id"]

    _create_stage_rule(client, admin_headers, eid, sid, item_name="S1")
    _create_stage_rule(client, admin_headers, eid, sid, item_name="S2")

    r = client.get(
        "/api/pricing-rules/stage",
        params={"estate_id": eid, "stage_id": sid},
        headers=admin_headers,
    )
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 2


def test_create_stage_rule(
    client: TestClient, admin_headers, sample_stages_and_lots
):
    eid = sample_stages_and_lots["estate_id"]
    sid = sample_stages_and_lots["stage_a_id"]
    r = _create_stage_rule(client, admin_headers, eid, sid)
    assert r.status_code == 201
    body = r.json()
    assert body["estate_id"] == eid
    assert body["stage_id"] == sid


def test_get_stage_rule(
    client: TestClient, admin_headers, sample_stages_and_lots
):
    eid = sample_stages_and_lots["estate_id"]
    sid = sample_stages_and_lots["stage_a_id"]
    r_create = _create_stage_rule(client, admin_headers, eid, sid)
    rule_id = r_create.json()["rule_id"]

    r = client.get(f"/api/pricing-rules/stage/{rule_id}", headers=admin_headers)
    assert r.status_code == 200
    assert r.json()["rule_id"] == rule_id


def test_update_stage_rule(
    client: TestClient, admin_headers, sample_stages_and_lots
):
    eid = sample_stages_and_lots["estate_id"]
    sid = sample_stages_and_lots["stage_a_id"]
    r_create = _create_stage_rule(client, admin_headers, eid, sid, item_name="Old")
    rule_id = r_create.json()["rule_id"]

    r = client.patch(
        f"/api/pricing-rules/stage/{rule_id}",
        json={"item_name": "Updated Stage"},
        headers=admin_headers,
    )
    assert r.status_code == 200
    assert r.json()["item_name"] == "Updated Stage"


def test_delete_stage_rule(
    client: TestClient, admin_headers, sample_stages_and_lots
):
    eid = sample_stages_and_lots["estate_id"]
    sid = sample_stages_and_lots["stage_a_id"]
    r_create = _create_stage_rule(client, admin_headers, eid, sid)
    rule_id = r_create.json()["rule_id"]

    r = client.delete(f"/api/pricing-rules/stage/{rule_id}", headers=admin_headers)
    assert r.status_code == 204


def test_duplicate_stage_rule(
    client: TestClient, admin_headers, sample_stages_and_lots
):
    eid = sample_stages_and_lots["estate_id"]
    sid = sample_stages_and_lots["stage_a_id"]
    r_create = _create_stage_rule(
        client, admin_headers, eid, sid, item_name="Stage Original"
    )
    rule_id = r_create.json()["rule_id"]

    r = client.post(
        f"/api/pricing-rules/stage/{rule_id}/duplicate",
        headers=admin_headers,
    )
    assert r.status_code == 201
    dup = r.json()
    assert dup["rule_id"] != rule_id
    assert dup["item_name"] == "Stage Original"


# =============================================================================
# Auth tests
# =============================================================================


def test_unauth_401_on_any_endpoint(client: TestClient, seeded_users):
    r = client.get("/api/pricing-rules/global", params={"brand": BRAND})
    assert r.status_code == 401

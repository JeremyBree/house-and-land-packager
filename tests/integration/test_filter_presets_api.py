"""Integration tests: /api/filter-presets CRUD (Sprint 3, user-scoped)."""
from __future__ import annotations

from fastapi.testclient import TestClient


def _make_preset_body(name: str, **filter_overrides) -> dict:
    filters = {
        "statuses": ["Available"],
        "price_min": 300000,
        "price_max": 500000,
        "exclude_null_price": True,
    }
    filters.update(filter_overrides)
    return {"name": name, "filters": filters}


# ------------------------ auth ----------------------------------------------


def test_unauthenticated_401(client: TestClient):
    r = client.get("/api/filter-presets")
    assert r.status_code == 401
    r2 = client.post("/api/filter-presets", json=_make_preset_body("x"))
    assert r2.status_code == 401


# ------------------------ create --------------------------------------------


def test_user_can_create_preset_201(
    client: TestClient, sales_headers, seeded_users
):
    r = client.post(
        "/api/filter-presets",
        json=_make_preset_body("My Preset"),
        headers=sales_headers,
    )
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["name"] == "My Preset"
    # Decimal values serialize as strings in JSONB via Pydantic mode=json.
    assert str(body["filters"]["price_min"]) in {"300000", "300000.00"}
    assert body["preset_id"] > 0


# ------------------------ list (user isolation) -----------------------------


def test_user_can_list_own_presets_only(
    client: TestClient,
    sales_headers,
    second_user_headers,
    seeded_users,
):
    # User A creates two presets.
    client.post(
        "/api/filter-presets",
        json=_make_preset_body("A1"),
        headers=sales_headers,
    )
    client.post(
        "/api/filter-presets",
        json=_make_preset_body("A2"),
        headers=sales_headers,
    )
    # User B creates one preset.
    client.post(
        "/api/filter-presets",
        json=_make_preset_body("B1"),
        headers=second_user_headers,
    )

    r_a = client.get("/api/filter-presets", headers=sales_headers)
    assert r_a.status_code == 200
    names_a = {p["name"] for p in r_a.json()}
    assert names_a == {"A1", "A2"}

    r_b = client.get("/api/filter-presets", headers=second_user_headers)
    assert r_b.status_code == 200
    names_b = {p["name"] for p in r_b.json()}
    assert names_b == {"B1"}


# ------------------------ get -----------------------------------------------


def test_user_can_get_own_preset_by_id(
    client: TestClient, sales_headers, seeded_users
):
    created = client.post(
        "/api/filter-presets",
        json=_make_preset_body("Get Me"),
        headers=sales_headers,
    ).json()
    preset_id = created["preset_id"]

    r = client.get(f"/api/filter-presets/{preset_id}", headers=sales_headers)
    assert r.status_code == 200
    assert r.json()["name"] == "Get Me"


def test_user_gets_404_for_other_users_preset(
    client: TestClient,
    sales_headers,
    second_user_headers,
    seeded_users,
):
    created = client.post(
        "/api/filter-presets",
        json=_make_preset_body("Private"),
        headers=sales_headers,
    ).json()
    preset_id = created["preset_id"]

    r = client.get(
        f"/api/filter-presets/{preset_id}", headers=second_user_headers
    )
    assert r.status_code == 404
    assert r.json()["code"] == "filter_preset_not_found"


# ------------------------ update --------------------------------------------


def test_user_can_update_own_preset(
    client: TestClient, sales_headers, seeded_users
):
    created = client.post(
        "/api/filter-presets",
        json=_make_preset_body("Old Name"),
        headers=sales_headers,
    ).json()
    preset_id = created["preset_id"]

    r = client.patch(
        f"/api/filter-presets/{preset_id}",
        json={"name": "New Name"},
        headers=sales_headers,
    )
    assert r.status_code == 200
    assert r.json()["name"] == "New Name"


def test_user_cannot_update_other_users_preset_404(
    client: TestClient,
    sales_headers,
    second_user_headers,
    seeded_users,
):
    created = client.post(
        "/api/filter-presets",
        json=_make_preset_body("Owner Only"),
        headers=sales_headers,
    ).json()
    preset_id = created["preset_id"]

    r = client.patch(
        f"/api/filter-presets/{preset_id}",
        json={"name": "Hacked"},
        headers=second_user_headers,
    )
    assert r.status_code == 404


# ------------------------ delete --------------------------------------------


def test_user_can_delete_own_preset_204(
    client: TestClient, sales_headers, seeded_users
):
    created = client.post(
        "/api/filter-presets",
        json=_make_preset_body("ToDelete"),
        headers=sales_headers,
    ).json()
    preset_id = created["preset_id"]

    r = client.delete(
        f"/api/filter-presets/{preset_id}", headers=sales_headers
    )
    assert r.status_code == 204

    # Verify it's gone.
    r2 = client.get(
        f"/api/filter-presets/{preset_id}", headers=sales_headers
    )
    assert r2.status_code == 404


def test_user_cannot_delete_other_users_preset_404(
    client: TestClient,
    sales_headers,
    second_user_headers,
    seeded_users,
):
    created = client.post(
        "/api/filter-presets",
        json=_make_preset_body("Protect"),
        headers=sales_headers,
    ).json()
    preset_id = created["preset_id"]

    r = client.delete(
        f"/api/filter-presets/{preset_id}", headers=second_user_headers
    )
    assert r.status_code == 404

    # Original owner can still access it.
    r2 = client.get(
        f"/api/filter-presets/{preset_id}", headers=sales_headers
    )
    assert r2.status_code == 200


# ------------------------ uniqueness ----------------------------------------


def test_duplicate_preset_name_returns_409(
    client: TestClient, sales_headers, seeded_users
):
    client.post(
        "/api/filter-presets",
        json=_make_preset_body("Dup"),
        headers=sales_headers,
    )
    r = client.post(
        "/api/filter-presets",
        json=_make_preset_body("Dup"),
        headers=sales_headers,
    )
    assert r.status_code == 409
    assert r.json()["code"] == "duplicate_preset_name"


def test_different_users_can_have_same_preset_name(
    client: TestClient,
    sales_headers,
    second_user_headers,
    seeded_users,
):
    r1 = client.post(
        "/api/filter-presets",
        json=_make_preset_body("Shared Name"),
        headers=sales_headers,
    )
    assert r1.status_code == 201
    r2 = client.post(
        "/api/filter-presets",
        json=_make_preset_body("Shared Name"),
        headers=second_user_headers,
    )
    assert r2.status_code == 201


# ------------------------ JSONB round-trip ----------------------------------


def test_preset_filters_stored_as_jsonb(
    client: TestClient, sales_headers, seeded_users
):
    body = _make_preset_body(
        "Full Filters",
        estate_ids=[1, 2, 3],
        suburbs=["Tarneit", "Werribee"],
        corner_block=True,
        text_search="acacia",
    )
    created = client.post(
        "/api/filter-presets", json=body, headers=sales_headers
    )
    assert created.status_code == 201
    preset_id = created.json()["preset_id"]

    r = client.get(
        f"/api/filter-presets/{preset_id}", headers=sales_headers
    )
    assert r.status_code == 200
    filters = r.json()["filters"]
    assert filters["estate_ids"] == [1, 2, 3]
    assert filters["suburbs"] == ["Tarneit", "Werribee"]
    assert filters["corner_block"] is True
    assert filters["text_search"] == "acacia"
    assert filters["statuses"] == ["Available"]

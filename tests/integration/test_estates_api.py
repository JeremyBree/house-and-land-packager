"""Integration tests: /api/estates endpoints."""
from __future__ import annotations

from fastapi.testclient import TestClient


# ---- list -----------------------------------------------------------------


def test_any_authenticated_user_lists_estates_200(
    client: TestClient, sales_headers, seeded_users, sample_data
):
    r = client.get("/api/estates", headers=sales_headers)
    assert r.status_code == 200
    body = r.json()
    assert body["page"] == 1
    assert isinstance(body["items"], list)
    # 5 estates seeded (including 1 inactive), default returns all unless
    # active is filtered.
    assert body["total"] == 5


def test_unauth_cannot_list_estates_401(client: TestClient):
    r = client.get("/api/estates")
    assert r.status_code == 401


def test_list_estates_filters_by_developer_id(
    client: TestClient, sales_headers, seeded_users, sample_data
):
    stockland_id = sample_data["developers"][0]["developer_id"]
    r = client.get(
        f"/api/estates?developer_id={stockland_id}",
        headers=sales_headers,
    )
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 3  # Cloverton, Highlands, Retired Estate
    for item in body["items"]:
        assert item["developer_id"] == stockland_id


def test_list_estates_filters_by_region_id(
    client: TestClient, sales_headers, seeded_users, sample_data
):
    north_id = sample_data["regions"][0]["region_id"]
    r = client.get(
        f"/api/estates?region_id={north_id}",
        headers=sales_headers,
    )
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 2  # Cloverton + Highlands


def test_list_estates_filters_by_active_true(
    client: TestClient, sales_headers, seeded_users, sample_data
):
    r = client.get("/api/estates?active=true", headers=sales_headers)
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 4
    for item in body["items"]:
        assert item["active"] is True


def test_list_estates_filters_by_active_false(
    client: TestClient, sales_headers, seeded_users, sample_data
):
    r = client.get("/api/estates?active=false", headers=sales_headers)
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 1
    assert body["items"][0]["estate_name"] == "Retired Estate"


def test_list_estates_search_by_name(
    client: TestClient, sales_headers, seeded_users, sample_data
):
    r = client.get("/api/estates?search=clover", headers=sales_headers)
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 1
    assert body["items"][0]["estate_name"] == "Cloverton"


def test_list_estates_search_by_suburb(
    client: TestClient, sales_headers, seeded_users, sample_data
):
    r = client.get("/api/estates?search=clyde", headers=sales_headers)
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 1
    assert body["items"][0]["estate_name"] == "Smiths Lane"


def test_list_estates_pagination(
    client: TestClient, sales_headers, seeded_users, sample_data
):
    r = client.get("/api/estates?page=1&size=2", headers=sales_headers)
    assert r.status_code == 200
    body = r.json()
    assert len(body["items"]) == 2
    assert body["size"] == 2
    assert body["pages"] == 3  # 5 items / size 2 = 3 pages

    r2 = client.get("/api/estates?page=3&size=2", headers=sales_headers)
    assert r2.status_code == 200
    assert len(r2.json()["items"]) == 1


# ---- get by id ------------------------------------------------------------


def test_get_estate_by_id_returns_detail_with_nested_relations(
    client: TestClient, sales_headers, seeded_users, sample_data
):
    estate_id = sample_data["estates"][0]["estate_id"]
    r = client.get(f"/api/estates/{estate_id}", headers=sales_headers)
    assert r.status_code == 200
    body = r.json()
    assert body["estate_name"] == "Cloverton"
    assert body["developer"]["developer_name"] == "Stockland"
    assert body["region"]["name"] == "North"


def test_get_missing_estate_returns_404(
    client: TestClient, sales_headers, seeded_users, sample_data
):
    r = client.get("/api/estates/999999", headers=sales_headers)
    assert r.status_code == 404
    assert r.json()["code"] == "not_found"


# ---- create ---------------------------------------------------------------


def _estate_payload(developer_id, region_id=None, **overrides):
    base = {
        "developer_id": developer_id,
        "region_id": region_id,
        "estate_name": "New Estate",
        "suburb": "Somewhere",
        "state": "VIC",
        "postcode": "3000",
    }
    base.update(overrides)
    return base


def test_admin_creates_estate_201(
    client: TestClient, admin_headers, seeded_users, sample_data
):
    did = sample_data["developers"][0]["developer_id"]
    rid = sample_data["regions"][0]["region_id"]
    r = client.post(
        "/api/estates",
        json=_estate_payload(did, rid, estate_name="Brand New"),
        headers=admin_headers,
    )
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["estate_name"] == "Brand New"
    assert body["developer"]["developer_id"] == did
    assert body["region"]["region_id"] == rid
    assert body["active"] is True


def test_admin_creates_estate_with_invalid_developer_fk_errors(
    client: TestClient, admin_headers, seeded_users, sample_data
):
    r = client.post(
        "/api/estates",
        json=_estate_payload(999999, estate_name="Orphan"),
        headers=admin_headers,
    )
    # FK violation — SQLite raises IntegrityError -> 500 via FastAPI default.
    assert r.status_code >= 400
    assert r.status_code != 201


def test_non_admin_cannot_create_estate_403(
    client: TestClient, sales_headers, seeded_users, sample_data
):
    did = sample_data["developers"][0]["developer_id"]
    r = client.post(
        "/api/estates",
        json=_estate_payload(did, estate_name="NopeEstate"),
        headers=sales_headers,
    )
    assert r.status_code == 403


# ---- update ---------------------------------------------------------------


def test_admin_updates_estate(
    client: TestClient, admin_headers, seeded_users, sample_data
):
    estate_id = sample_data["estates"][0]["estate_id"]
    r = client.patch(
        f"/api/estates/{estate_id}",
        json={"suburb": "New Suburb", "notes": "updated"},
        headers=admin_headers,
    )
    assert r.status_code == 200
    body = r.json()
    assert body["suburb"] == "New Suburb"
    assert body["notes"] == "updated"


def test_non_admin_cannot_update_estate_403(
    client: TestClient, sales_headers, seeded_users, sample_data
):
    estate_id = sample_data["estates"][0]["estate_id"]
    r = client.patch(
        f"/api/estates/{estate_id}",
        json={"suburb": "No Way"},
        headers=sales_headers,
    )
    assert r.status_code == 403


# ---- delete (soft) --------------------------------------------------------


def test_admin_soft_deletes_estate_204(
    client: TestClient, admin_headers, seeded_users, sample_data
):
    estate_id = sample_data["estates"][0]["estate_id"]
    r = client.delete(f"/api/estates/{estate_id}", headers=admin_headers)
    assert r.status_code == 204

    # Record still exists, just flipped to active=false.
    r2 = client.get(f"/api/estates/{estate_id}", headers=admin_headers)
    assert r2.status_code == 200
    assert r2.json()["active"] is False


def test_deleted_estate_hidden_from_active_list(
    client: TestClient, admin_headers, seeded_users, sample_data
):
    estate_id = sample_data["estates"][1]["estate_id"]  # Highlands
    client.delete(f"/api/estates/{estate_id}", headers=admin_headers)

    r = client.get("/api/estates?active=true", headers=admin_headers)
    assert r.status_code == 200
    ids = {item["estate_id"] for item in r.json()["items"]}
    assert estate_id not in ids


def test_non_admin_cannot_delete_estate_403(
    client: TestClient, sales_headers, seeded_users, sample_data
):
    estate_id = sample_data["estates"][0]["estate_id"]
    r = client.delete(f"/api/estates/{estate_id}", headers=sales_headers)
    assert r.status_code == 403

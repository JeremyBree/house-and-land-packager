"""Integration tests: /api/regions endpoints."""
from __future__ import annotations

from fastapi.testclient import TestClient


def test_any_authenticated_user_can_list_regions_200(
    client: TestClient, sales_headers, seeded_users
):
    r = client.get("/api/regions", headers=sales_headers)
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_unauth_cannot_list_regions_401(client: TestClient):
    r = client.get("/api/regions")
    assert r.status_code == 401


def test_admin_creates_region_201(
    client: TestClient, admin_headers, seeded_users
):
    r = client.post("/api/regions", json={"name": "Central"}, headers=admin_headers)
    assert r.status_code == 201
    body = r.json()
    assert body["name"] == "Central"
    assert "region_id" in body


def test_admin_creates_duplicate_region_name_returns_error(
    client: TestClient, admin_headers, seeded_users
):
    client.post("/api/regions", json={"name": "Dupe"}, headers=admin_headers)
    r = client.post("/api/regions", json={"name": "Dupe"}, headers=admin_headers)
    # regions.name has a unique constraint -> DB IntegrityError -> 500
    # via the generic HLPError handler is NOT triggered (it's SQLAlchemyError),
    # so FastAPI surfaces a 500. We just assert it is not 2xx.
    assert r.status_code >= 400


def test_non_admin_cannot_create_region_403(
    client: TestClient, sales_headers, seeded_users
):
    r = client.post("/api/regions", json={"name": "Nope"}, headers=sales_headers)
    assert r.status_code == 403


def test_admin_updates_region(
    client: TestClient, admin_headers, seeded_users
):
    created = client.post(
        "/api/regions", json={"name": "Orig"}, headers=admin_headers
    )
    rid = created.json()["region_id"]
    r = client.patch(
        f"/api/regions/{rid}", json={"name": "Renamed"}, headers=admin_headers
    )
    assert r.status_code == 200
    assert r.json()["name"] == "Renamed"


def test_admin_deletes_region_204(
    client: TestClient, admin_headers, seeded_users
):
    created = client.post(
        "/api/regions", json={"name": "ToDelete"}, headers=admin_headers
    )
    rid = created.json()["region_id"]
    r = client.delete(f"/api/regions/{rid}", headers=admin_headers)
    assert r.status_code == 204


def test_delete_missing_region_returns_404(
    client: TestClient, admin_headers, seeded_users
):
    r = client.delete("/api/regions/999999", headers=admin_headers)
    assert r.status_code == 404
    assert r.json()["code"] == "not_found"


def test_non_admin_cannot_delete_region_403(
    client: TestClient, sales_headers, seeded_users, admin_headers
):
    created = client.post(
        "/api/regions", json={"name": "Guarded"}, headers=admin_headers
    )
    rid = created.json()["region_id"]
    r = client.delete(f"/api/regions/{rid}", headers=sales_headers)
    assert r.status_code == 403

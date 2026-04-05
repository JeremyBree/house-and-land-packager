"""Integration tests: /api/developers endpoints."""
from __future__ import annotations

from fastapi.testclient import TestClient


def _payload(**overrides):
    base = {
        "developer_name": "Stockland",
        "developer_website": "https://stockland.example",
        "contact_email": "ops@stockland.example",
        "notes": "seed",
    }
    base.update(overrides)
    return base


def test_any_authenticated_user_can_list_developers_200(
    client: TestClient, pricing_headers, seeded_users
):
    r = client.get("/api/developers", headers=pricing_headers)
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_unauth_cannot_list_developers_401(client: TestClient):
    r = client.get("/api/developers")
    assert r.status_code == 401


def test_admin_creates_developer_201(
    client: TestClient, admin_headers, seeded_users
):
    r = client.post(
        "/api/developers",
        json=_payload(developer_name="NewDev"),
        headers=admin_headers,
    )
    assert r.status_code == 201
    body = r.json()
    assert body["developer_name"] == "NewDev"
    assert body["contact_email"] == "ops@stockland.example"
    assert "developer_id" in body


def test_admin_creates_developer_with_invalid_email_returns_422(
    client: TestClient, admin_headers, seeded_users
):
    r = client.post(
        "/api/developers",
        json=_payload(developer_name="BadEmail", contact_email="not-an-email"),
        headers=admin_headers,
    )
    assert r.status_code == 422


def test_non_admin_cannot_create_developer_403(
    client: TestClient, sales_headers, seeded_users
):
    r = client.post(
        "/api/developers", json=_payload(developer_name="X"), headers=sales_headers
    )
    assert r.status_code == 403


def test_admin_updates_developer(
    client: TestClient, admin_headers, seeded_users
):
    created = client.post(
        "/api/developers",
        json=_payload(developer_name="Initial"),
        headers=admin_headers,
    )
    did = created.json()["developer_id"]
    r = client.patch(
        f"/api/developers/{did}",
        json={"developer_name": "Updated", "notes": "new notes"},
        headers=admin_headers,
    )
    assert r.status_code == 200
    body = r.json()
    assert body["developer_name"] == "Updated"
    assert body["notes"] == "new notes"


def test_admin_deletes_developer_204(
    client: TestClient, admin_headers, seeded_users
):
    created = client.post(
        "/api/developers",
        json=_payload(developer_name="Disposable"),
        headers=admin_headers,
    )
    did = created.json()["developer_id"]
    r = client.delete(f"/api/developers/{did}", headers=admin_headers)
    assert r.status_code == 204


def test_delete_missing_developer_returns_404(
    client: TestClient, admin_headers, seeded_users
):
    r = client.delete("/api/developers/999999", headers=admin_headers)
    assert r.status_code == 404
    assert r.json()["code"] == "not_found"


def test_non_admin_cannot_delete_developer_403(
    client: TestClient, sales_headers, admin_headers, seeded_users
):
    created = client.post(
        "/api/developers",
        json=_payload(developer_name="Guarded"),
        headers=admin_headers,
    )
    did = created.json()["developer_id"]
    r = client.delete(f"/api/developers/{did}", headers=sales_headers)
    assert r.status_code == 403

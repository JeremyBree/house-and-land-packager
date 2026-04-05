"""Integration tests: /api/users endpoints (admin-only)."""
from __future__ import annotations

from fastapi.testclient import TestClient


# ---- list / search --------------------------------------------------------


def test_admin_can_list_users(client: TestClient, admin_headers, seeded_users):
    r = client.get("/api/users", headers=admin_headers)
    assert r.status_code == 200
    body = r.json()
    assert body["total"] >= 4
    assert body["page"] == 1
    assert body["size"] == 25
    assert isinstance(body["items"], list)


def test_admin_can_search_users(client: TestClient, admin_headers, seeded_users):
    r = client.get("/api/users?search=sales", headers=admin_headers)
    assert r.status_code == 200
    body = r.json()
    assert body["total"] >= 1
    emails = {item["email"] for item in body["items"]}
    assert "sales@it.example.com" in emails


def test_admin_pagination(client: TestClient, admin_headers, seeded_users):
    r = client.get("/api/users?page=1&size=2", headers=admin_headers)
    assert r.status_code == 200
    body = r.json()
    assert len(body["items"]) == 2
    assert body["size"] == 2


def test_sales_cannot_list_users_403(client: TestClient, sales_headers, seeded_users):
    r = client.get("/api/users", headers=sales_headers)
    assert r.status_code == 403
    assert r.json()["code"] == "not_authorized"


def test_unauthenticated_cannot_list_users_401(client: TestClient):
    r = client.get("/api/users")
    assert r.status_code == 401


# ---- create ---------------------------------------------------------------


def _new_user_payload(**overrides):
    base = {
        "email": "fresh@it.example.com",
        "password": "Fresh1234!",
        "first_name": "Fresh",
        "last_name": "User",
        "job_title": "Fresher",
        "roles": ["sales"],
    }
    base.update(overrides)
    return base


def test_admin_creates_user_201(client: TestClient, admin_headers, seeded_users):
    r = client.post("/api/users", json=_new_user_payload(), headers=admin_headers)
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["email"] == "fresh@it.example.com"
    assert body["roles"] == ["sales"]
    assert "profile_id" in body


def test_admin_creates_duplicate_email_returns_409(
    client: TestClient, admin_headers, seeded_users
):
    r = client.post(
        "/api/users",
        json=_new_user_payload(email="admin@it.example.com"),
        headers=admin_headers,
    )
    assert r.status_code == 409
    assert r.json()["code"] == "duplicate_email"


def test_admin_creates_user_without_roles_returns_422(
    client: TestClient, admin_headers, seeded_users
):
    # Pydantic schema enforces min_length=1 on roles, so this is a 422 at the
    # validation layer rather than a 400 from MinRolesRequiredError.
    r = client.post(
        "/api/users",
        json=_new_user_payload(email="no_roles@it.example.com", roles=[]),
        headers=admin_headers,
    )
    assert r.status_code == 422


def test_admin_creates_user_with_invalid_email_format_returns_422(
    client: TestClient, admin_headers, seeded_users
):
    r = client.post(
        "/api/users",
        json=_new_user_payload(email="not-an-email"),
        headers=admin_headers,
    )
    assert r.status_code == 422


def test_admin_creates_user_with_short_password_returns_422(
    client: TestClient, admin_headers, seeded_users
):
    r = client.post(
        "/api/users",
        json=_new_user_payload(email="short@it.example.com", password="short"),
        headers=admin_headers,
    )
    assert r.status_code == 422


def test_non_admin_cannot_create_user_403(
    client: TestClient, sales_headers, seeded_users
):
    r = client.post(
        "/api/users",
        json=_new_user_payload(email="nope@it.example.com"),
        headers=sales_headers,
    )
    assert r.status_code == 403


# ---- get ------------------------------------------------------------------


def test_admin_gets_user_by_id_200(
    client: TestClient, admin_headers, seeded_users
):
    pid = seeded_users["sales"]["profile_id"]
    r = client.get(f"/api/users/{pid}", headers=admin_headers)
    assert r.status_code == 200
    body = r.json()
    assert body["profile_id"] == pid
    assert body["email"] == "sales@it.example.com"


def test_admin_gets_missing_user_returns_404(
    client: TestClient, admin_headers, seeded_users
):
    r = client.get("/api/users/999999", headers=admin_headers)
    assert r.status_code == 404
    assert r.json()["code"] == "user_not_found"


# ---- update ---------------------------------------------------------------


def test_admin_updates_user_profile_fields(
    client: TestClient, admin_headers, seeded_users
):
    pid = seeded_users["sales"]["profile_id"]
    r = client.patch(
        f"/api/users/{pid}",
        json={"first_name": "Updated", "job_title": "Director"},
        headers=admin_headers,
    )
    assert r.status_code == 200
    body = r.json()
    assert body["first_name"] == "Updated"
    assert body["job_title"] == "Director"
    # last_name should be untouched.
    assert body["last_name"] == "User"


def test_admin_updates_user_roles_replaces_all(
    client: TestClient, admin_headers, seeded_users
):
    pid = seeded_users["sales"]["profile_id"]
    r = client.put(
        f"/api/users/{pid}/roles",
        json={"roles": ["admin", "pricing"]},
        headers=admin_headers,
    )
    assert r.status_code == 200
    body = r.json()
    assert set(body["roles"]) == {"admin", "pricing"}

    # Verify via GET.
    r2 = client.get(f"/api/users/{pid}", headers=admin_headers)
    assert set(r2.json()["roles"]) == {"admin", "pricing"}


def test_admin_updates_user_to_zero_roles_returns_422(
    client: TestClient, admin_headers, seeded_users
):
    pid = seeded_users["sales"]["profile_id"]
    r = client.put(
        f"/api/users/{pid}/roles",
        json={"roles": []},
        headers=admin_headers,
    )
    # min_length=1 schema constraint -> 422 at validation.
    assert r.status_code == 422


# ---- delete ---------------------------------------------------------------


def test_admin_deletes_user_204(
    client: TestClient, admin_headers, seeded_users
):
    # Create a disposable user so we don't disturb other fixtures.
    created = client.post(
        "/api/users",
        json=_new_user_payload(email="todelete@it.example.com"),
        headers=admin_headers,
    )
    assert created.status_code == 201
    pid = created.json()["profile_id"]

    r = client.delete(f"/api/users/{pid}", headers=admin_headers)
    assert r.status_code == 204

    # Subsequent GET should 404.
    r2 = client.get(f"/api/users/{pid}", headers=admin_headers)
    assert r2.status_code == 404


def test_admin_deletes_user_cascade_removes_user_roles(
    client: TestClient, admin_headers, seeded_users, _session_factory
):
    created = client.post(
        "/api/users",
        json=_new_user_payload(
            email="cascade@it.example.com", roles=["admin", "pricing"]
        ),
        headers=admin_headers,
    )
    assert created.status_code == 201
    pid = created.json()["profile_id"]

    r = client.delete(f"/api/users/{pid}", headers=admin_headers)
    assert r.status_code == 204

    from hlp.models.user_role import UserRole

    session = _session_factory()
    try:
        rows = session.query(UserRole).filter_by(profile_id=pid).all()
        assert rows == []
    finally:
        session.close()

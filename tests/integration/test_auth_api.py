"""Integration tests: /api/auth endpoints."""
from __future__ import annotations

from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient
from jose import jwt

from hlp.config import get_settings


def test_login_valid_credentials_returns_token(client: TestClient, seeded_users):
    r = client.post(
        "/api/auth/login",
        data={"username": "admin@it.example.com", "password": "Admin1234!"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]
    assert body["expires_in"] > 0


def test_login_wrong_password_returns_401(client: TestClient, seeded_users):
    r = client.post(
        "/api/auth/login",
        data={"username": "admin@it.example.com", "password": "wrong"},
    )
    assert r.status_code == 401
    assert r.json()["code"] == "authentication_error"


def test_login_unknown_email_returns_401(client: TestClient, seeded_users):
    r = client.post(
        "/api/auth/login",
        data={"username": "ghost@it.example.com", "password": "doesntmatter"},
    )
    assert r.status_code == 401
    assert r.json()["code"] == "authentication_error"


def test_login_malformed_request_returns_422(client: TestClient):
    r = client.post("/api/auth/login", data={})
    assert r.status_code == 422


def test_me_with_valid_token_returns_user(
    client: TestClient, admin_headers, seeded_users
):
    r = client.get("/api/auth/me", headers=admin_headers)
    assert r.status_code == 200
    body = r.json()
    assert body["email"] == "admin@it.example.com"
    assert "admin" in body["roles"]
    assert body["first_name"] == "Admin"


def test_me_without_token_returns_401(client: TestClient):
    r = client.get("/api/auth/me")
    assert r.status_code == 401


def test_me_with_tampered_token_returns_401(
    client: TestClient, admin_token: str
):
    tampered = admin_token[:-4] + ("AAAA" if admin_token[-4:] != "AAAA" else "BBBB")
    r = client.get("/api/auth/me", headers={"Authorization": f"Bearer {tampered}"})
    assert r.status_code == 401
    assert r.json()["code"] == "authentication_error"


def test_me_with_expired_token_returns_401(client: TestClient, seeded_users):
    settings = get_settings()
    now = datetime.now(UTC)
    expired = jwt.encode(
        {
            "sub": str(seeded_users["admin"]["profile_id"]),
            "email": seeded_users["admin"]["email"],
            "roles": ["admin"],
            "exp": now - timedelta(minutes=5),
            "iat": now - timedelta(minutes=60),
        },
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )
    r = client.get("/api/auth/me", headers={"Authorization": f"Bearer {expired}"})
    assert r.status_code == 401


def test_me_with_gibberish_token_returns_401(client: TestClient):
    r = client.get(
        "/api/auth/me", headers={"Authorization": "Bearer not.a.jwt"}
    )
    assert r.status_code == 401

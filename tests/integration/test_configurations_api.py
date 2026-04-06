"""Integration tests: /api/configurations endpoints."""
from __future__ import annotations

from fastapi.testclient import TestClient

from tests.integration.conftest import auth_header


def _create_config(client: TestClient, headers: dict, **overrides) -> dict:
    payload = {
        "config_type": "website",
        "label": "Test Config",
        "url_or_path": "https://example.com/lots",
        "enabled": True,
        "priority_rank": 0,
        "scraping_config": {},
        **overrides,
    }
    r = client.post("/api/configurations", json=payload, headers=headers)
    assert r.status_code == 201, r.text
    return r.json()


def test_admin_lists_configurations(
    client: TestClient, admin_headers, seeded_users
):
    _create_config(client, admin_headers, label="Config A")
    _create_config(client, admin_headers, label="Config B")
    r = client.get("/api/configurations", headers=admin_headers)
    assert r.status_code == 200
    body = r.json()
    assert len(body) >= 2


def test_admin_creates_configuration(
    client: TestClient, admin_headers, seeded_users
):
    cfg = _create_config(client, admin_headers, label="New Config")
    assert cfg["label"] == "New Config"
    assert cfg["config_type"] == "website"
    assert cfg["enabled"] is True


def test_admin_updates_configuration(
    client: TestClient, admin_headers, seeded_users
):
    cfg = _create_config(client, admin_headers)
    r = client.patch(
        f"/api/configurations/{cfg['config_id']}",
        json={"label": "Updated Label"},
        headers=admin_headers,
    )
    assert r.status_code == 200
    assert r.json()["label"] == "Updated Label"


def test_admin_deletes_configuration_204(
    client: TestClient, admin_headers, seeded_users
):
    cfg = _create_config(client, admin_headers)
    r = client.delete(
        f"/api/configurations/{cfg['config_id']}",
        headers=admin_headers,
    )
    assert r.status_code == 204

    r2 = client.get(
        f"/api/configurations/{cfg['config_id']}",
        headers=admin_headers,
    )
    assert r2.status_code == 404


def test_admin_toggles_enabled(
    client: TestClient, admin_headers, seeded_users
):
    cfg = _create_config(client, admin_headers, enabled=True)
    assert cfg["enabled"] is True

    r = client.post(
        f"/api/configurations/{cfg['config_id']}/toggle",
        headers=admin_headers,
    )
    assert r.status_code == 200
    assert r.json()["enabled"] is False

    r2 = client.post(
        f"/api/configurations/{cfg['config_id']}/toggle",
        headers=admin_headers,
    )
    assert r2.status_code == 200
    assert r2.json()["enabled"] is True


def test_credentials_ref_masked_in_response(
    client: TestClient, admin_headers, seeded_users
):
    cfg = _create_config(
        client, admin_headers,
        credentials_ref="SECRET_ENV_VAR",
    )
    assert cfg["credentials_ref"] == "[configured]"

    r = client.get(
        f"/api/configurations/{cfg['config_id']}",
        headers=admin_headers,
    )
    assert r.json()["credentials_ref"] == "[configured]"


def test_list_filter_by_type(
    client: TestClient, admin_headers, seeded_users
):
    _create_config(client, admin_headers, config_type="website", label="Web1")
    _create_config(client, admin_headers, config_type="email_account", label="Email1")

    r = client.get("/api/configurations?type=website", headers=admin_headers)
    assert r.status_code == 200
    body = r.json()
    assert all(c["config_type"] == "website" for c in body)


def test_list_filter_by_enabled(
    client: TestClient, admin_headers, seeded_users
):
    _create_config(client, admin_headers, enabled=True, label="Enabled1")
    _create_config(client, admin_headers, enabled=False, label="Disabled1")

    r = client.get("/api/configurations?enabled=true", headers=admin_headers)
    assert r.status_code == 200
    body = r.json()
    assert all(c["enabled"] is True for c in body)


def test_non_admin_403(
    client: TestClient, sales_headers, seeded_users
):
    r = client.get("/api/configurations", headers=sales_headers)
    assert r.status_code == 403


def test_unauth_401(client: TestClient):
    r = client.get("/api/configurations")
    assert r.status_code == 401

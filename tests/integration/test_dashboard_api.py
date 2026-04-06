"""Integration tests: /api/dashboard endpoint."""
from __future__ import annotations

from fastapi.testclient import TestClient

from tests.integration.conftest import auth_header


def test_dashboard_returns_counts(
    client: TestClient, admin_headers, seeded_users, sample_data
):
    r = client.get("/api/dashboard", headers=admin_headers)
    assert r.status_code == 200
    body = r.json()
    assert body["total_estates"] >= 1
    assert "total_lots" in body
    assert "total_packages" in body
    assert "active_conflicts" in body
    assert "pending_requests" in body
    assert isinstance(body["lot_status_breakdown"], dict)
    assert isinstance(body["recent_requests"], list)


def test_dashboard_lot_status_breakdown_sums_correctly(
    client: TestClient, admin_headers, seeded_users, sample_stages_and_lots
):
    r = client.get("/api/dashboard", headers=admin_headers)
    assert r.status_code == 200
    body = r.json()
    breakdown = body["lot_status_breakdown"]
    total_from_breakdown = sum(breakdown.values())
    assert total_from_breakdown == body["total_lots"]


def test_dashboard_recent_requests_limit(
    client: TestClient, admin_headers, seeded_users, sample_data
):
    """Recent requests should return at most 5 items."""
    r = client.get("/api/dashboard", headers=admin_headers)
    assert r.status_code == 200
    body = r.json()
    assert len(body["recent_requests"]) <= 5


def test_dashboard_unauthenticated_401(client: TestClient):
    r = client.get("/api/dashboard")
    assert r.status_code == 401


def test_dashboard_any_role_can_access(
    client: TestClient, sales_headers, seeded_users, sample_data
):
    r = client.get("/api/dashboard", headers=sales_headers)
    assert r.status_code == 200
    body = r.json()
    assert "total_estates" in body

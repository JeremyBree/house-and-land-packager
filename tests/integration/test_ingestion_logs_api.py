"""Integration tests: /api/ingestion-logs endpoints."""
from __future__ import annotations

from datetime import datetime, timezone

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from tests.integration.conftest import auth_header


def _seed_logs(session_factory):
    """Insert sample ingestion log records directly."""
    from hlp.models.ingestion_log import IngestionLog

    session: Session = session_factory()
    try:
        logs = [
            IngestionLog(
                agent_type="email",
                source_identifier="inbox@example.com",
                records_found=10,
                records_created=5,
                records_updated=3,
                records_deactivated=2,
                status="success",
            ),
            IngestionLog(
                agent_type="scraper",
                source_identifier="https://dev.com/lots",
                records_found=20,
                records_created=15,
                records_updated=5,
                records_deactivated=0,
                status="success",
            ),
            IngestionLog(
                agent_type="portal",
                source_identifier="portal-api",
                records_found=5,
                records_created=2,
                records_updated=1,
                records_deactivated=0,
                status="partial",
            ),
            IngestionLog(
                agent_type="pdf",
                source_identifier="/data/uploads/plan.pdf",
                records_found=0,
                records_created=0,
                records_updated=0,
                records_deactivated=0,
                status="failed",
                error_detail="PDF parsing error: corrupted file",
            ),
        ]
        session.add_all(logs)
        session.commit()
        return [lg.log_id for lg in logs]
    finally:
        session.close()


def test_admin_lists_logs_paginated(
    client: TestClient, admin_headers, seeded_users, _session_factory
):
    _seed_logs(_session_factory)
    r = client.get("/api/ingestion-logs?page=1&size=2", headers=admin_headers)
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 4
    assert len(body["items"]) == 2
    assert body["page"] == 1
    assert body["pages"] == 2


def test_admin_gets_log_detail_with_error(
    client: TestClient, admin_headers, seeded_users, _session_factory
):
    log_ids = _seed_logs(_session_factory)
    failed_id = log_ids[-1]  # The failed PDF log
    r = client.get(f"/api/ingestion-logs/{failed_id}", headers=admin_headers)
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "failed"
    assert "PDF parsing error" in body["error_detail"]


def test_filter_by_agent_type(
    client: TestClient, admin_headers, seeded_users, _session_factory
):
    _seed_logs(_session_factory)
    r = client.get("/api/ingestion-logs?agent_type=email", headers=admin_headers)
    assert r.status_code == 200
    body = r.json()
    assert body["total"] >= 1
    assert all(item["agent_type"] == "email" for item in body["items"])


def test_filter_by_status(
    client: TestClient, admin_headers, seeded_users, _session_factory
):
    _seed_logs(_session_factory)
    r = client.get("/api/ingestion-logs?status=failed", headers=admin_headers)
    assert r.status_code == 200
    body = r.json()
    assert body["total"] >= 1
    assert all(item["status"] == "failed" for item in body["items"])


def test_non_admin_403(
    client: TestClient, sales_headers, seeded_users
):
    r = client.get("/api/ingestion-logs", headers=sales_headers)
    assert r.status_code == 403

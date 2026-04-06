"""Integration tests: /api/notifications endpoints."""

from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from tests.integration.conftest import auth_header


def _seed_notifications(session_factory, profile_id: int, count: int = 5):
    """Seed notifications for a profile."""
    from hlp.models.notification import Notification
    from hlp.models.pricing_request import PricingRequest
    from hlp.models.enums import PricingRequestStatus
    from hlp.models.developer import Developer
    from hlp.models.estate import Estate
    from hlp.models.estate_stage import EstateStage

    session: Session = session_factory()
    try:
        # Create minimal estate/stage for FK
        dev = Developer(developer_name="TestDev")
        session.add(dev)
        session.flush()
        estate = Estate(developer_id=dev.developer_id, estate_name="TestEstate")
        session.add(estate)
        session.flush()
        stage = EstateStage(estate_id=estate.estate_id, name="Stage 1")
        session.add(stage)
        session.flush()

        # Create a pricing request for FK
        req = PricingRequest(
            requester_id=profile_id,
            estate_id=estate.estate_id,
            stage_id=stage.stage_id,
            brand="Hermitage Homes",
            status=PricingRequestStatus.COMPLETED,
            form_data={},
            lot_numbers=["1"],
        )
        session.add(req)
        session.flush()

        notifs = []
        for i in range(count):
            n = Notification(
                profile_id=profile_id,
                pricing_request_id=req.request_id,
                title=f"Test notification {i + 1}",
                message=f"Message {i + 1}",
                read=(i >= 3),  # First 3 unread, rest read
            )
            session.add(n)
            notifs.append(n)
        session.commit()
        return {
            "request_id": req.request_id,
            "notification_ids": [n.notification_id for n in notifs],
        }
    finally:
        session.close()


def test_list_notifications_paginated(
    client: TestClient,
    admin_headers,
    seeded_users,
    _session_factory,
):
    profile_id = seeded_users["admin"]["profile_id"]
    _seed_notifications(_session_factory, profile_id, count=5)

    r = client.get("/api/notifications?page=1&size=3", headers=admin_headers)
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 5
    assert len(body["items"]) == 3
    assert body["page"] == 1
    assert body["size"] == 3


def test_unread_count(
    client: TestClient,
    admin_headers,
    seeded_users,
    _session_factory,
):
    profile_id = seeded_users["admin"]["profile_id"]
    _seed_notifications(_session_factory, profile_id, count=5)

    r = client.get("/api/notifications/unread-count", headers=admin_headers)
    assert r.status_code == 200
    body = r.json()
    assert body["count"] == 3  # First 3 are unread


def test_mark_read(
    client: TestClient,
    admin_headers,
    seeded_users,
    _session_factory,
):
    profile_id = seeded_users["admin"]["profile_id"]
    data = _seed_notifications(_session_factory, profile_id, count=5)

    # Mark first notification as read
    notif_id = data["notification_ids"][0]
    r = client.post(f"/api/notifications/{notif_id}/read", headers=admin_headers)
    assert r.status_code == 200
    body = r.json()
    assert body["read"] is True

    # Unread count should decrease
    r = client.get("/api/notifications/unread-count", headers=admin_headers)
    assert r.json()["count"] == 2


def test_mark_all_read(
    client: TestClient,
    admin_headers,
    seeded_users,
    _session_factory,
):
    profile_id = seeded_users["admin"]["profile_id"]
    _seed_notifications(_session_factory, profile_id, count=5)

    r = client.post("/api/notifications/read-all", headers=admin_headers)
    assert r.status_code == 200
    body = r.json()
    assert body["updated"] == 3  # 3 were unread

    # Verify all are now read
    r = client.get("/api/notifications/unread-count", headers=admin_headers)
    assert r.json()["count"] == 0


def test_user_sees_only_own_notifications(
    client: TestClient,
    admin_headers,
    sales_headers,
    seeded_users,
    _session_factory,
):
    admin_id = seeded_users["admin"]["profile_id"]
    _seed_notifications(_session_factory, admin_id, count=3)

    # Admin sees notifications
    r = client.get("/api/notifications", headers=admin_headers)
    assert r.status_code == 200
    assert r.json()["total"] == 3

    # Sales sees no notifications (none were created for them)
    r = client.get("/api/notifications", headers=sales_headers)
    assert r.status_code == 200
    assert r.json()["total"] == 0


def test_unauth_401(client: TestClient):
    r = client.get("/api/notifications")
    assert r.status_code == 401

    r = client.get("/api/notifications/unread-count")
    assert r.status_code == 401

    r = client.post("/api/notifications/read-all")
    assert r.status_code == 401

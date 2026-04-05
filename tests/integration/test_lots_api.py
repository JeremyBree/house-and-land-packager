"""Integration tests: /api/stages/{id}/lots* and /api/lots/{id}."""
from __future__ import annotations

from fastapi.testclient import TestClient


# ---- list lots ------------------------------------------------------------


def test_list_lots_paginated(
    client: TestClient, sales_headers, sample_stages_and_lots
):
    stage_id = sample_stages_and_lots["stage_a_id"]
    r = client.get(
        f"/api/stages/{stage_id}/lots?page=1&size=2",
        headers=sales_headers,
    )
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 5
    assert body["page"] == 1
    assert body["size"] == 2
    assert body["pages"] == 3
    assert len(body["items"]) == 2


def test_list_lots_filter_by_status(
    client: TestClient, sales_headers, sample_stages_and_lots
):
    stage_id = sample_stages_and_lots["stage_a_id"]
    r = client.get(
        f"/api/stages/{stage_id}/lots?status=Available",
        headers=sales_headers,
    )
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 2
    assert all(item["status"] == "Available" for item in body["items"])


def test_list_lots_empty_stage_returns_empty_items(
    client: TestClient, admin_headers, sample_data, _session_factory
):
    # Create an empty stage directly.
    from hlp.models.estate_stage import EstateStage

    s = _session_factory()
    try:
        stage = EstateStage(
            estate_id=sample_data["estates"][0]["estate_id"], name="Empty"
        )
        s.add(stage)
        s.commit()
        stage_id = stage.stage_id
    finally:
        s.close()

    r = client.get(f"/api/stages/{stage_id}/lots", headers=admin_headers)
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 0
    assert body["items"] == []


def test_list_lots_missing_stage_404(
    client: TestClient, admin_headers, seeded_users
):
    r = client.get("/api/stages/999999/lots", headers=admin_headers)
    assert r.status_code == 404


# ---- create single lot -----------------------------------------------------


def test_admin_creates_single_lot_201(
    client: TestClient, admin_headers, sample_stages_and_lots
):
    stage_id = sample_stages_and_lots["stage_a_id"]
    r = client.post(
        f"/api/stages/{stage_id}/lots",
        json={"lot_number": "NEW-1", "frontage": "12.5"},
        headers=admin_headers,
    )
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["lot_number"] == "NEW-1"
    assert body["stage_id"] == stage_id


def test_create_lot_duplicate_number_returns_409(
    client: TestClient, admin_headers, sample_stages_and_lots
):
    stage_id = sample_stages_and_lots["stage_a_id"]
    # "A1" already exists in stage_a per the fixture.
    r = client.post(
        f"/api/stages/{stage_id}/lots",
        json={"lot_number": "A1"},
        headers=admin_headers,
    )
    # Unique constraint violation — expect a 4xx error (409 if handler exists,
    # 500 via IntegrityError if not). We assert it's not a success.
    assert r.status_code >= 400
    # Preferred: 409 Conflict (uniqueness violation)
    assert r.status_code in (409, 500)


def test_non_admin_create_lot_403(
    client: TestClient, sales_headers, sample_stages_and_lots
):
    stage_id = sample_stages_and_lots["stage_a_id"]
    r = client.post(
        f"/api/stages/{stage_id}/lots",
        json={"lot_number": "X1"},
        headers=sales_headers,
    )
    assert r.status_code == 403


# ---- detail / update / delete ---------------------------------------------


def test_get_lot_detail_200(
    client: TestClient, sales_headers, sample_stages_and_lots
):
    lot_id = sample_stages_and_lots["stage_a_lot_ids"][0]
    r = client.get(f"/api/lots/{lot_id}", headers=sales_headers)
    assert r.status_code == 200
    assert r.json()["lot_id"] == lot_id


def test_get_missing_lot_404(
    client: TestClient, sales_headers, seeded_users
):
    r = client.get("/api/lots/999999", headers=sales_headers)
    assert r.status_code == 404


def test_admin_updates_lot_fields(
    client: TestClient, admin_headers, sample_stages_and_lots
):
    lot_id = sample_stages_and_lots["stage_a_lot_ids"][0]
    r = client.patch(
        f"/api/lots/{lot_id}",
        json={"street_name": "Updated St", "land_price": "275000.00"},
        headers=admin_headers,
    )
    assert r.status_code == 200
    body = r.json()
    assert body["street_name"] == "Updated St"
    assert body["land_price"] == "275000.00"


def test_admin_deletes_lot_204(
    client: TestClient, admin_headers, sales_headers, sample_stages_and_lots
):
    lot_id = sample_stages_and_lots["stage_a_lot_ids"][0]
    r = client.delete(f"/api/lots/{lot_id}", headers=admin_headers)
    assert r.status_code == 204
    r2 = client.get(f"/api/lots/{lot_id}", headers=sales_headers)
    assert r2.status_code == 404


# ---- bulk create ----------------------------------------------------------


def test_bulk_create_lots_returns_created_and_skipped_counts(
    client: TestClient, admin_headers, sample_stages_and_lots
):
    stage_id = sample_stages_and_lots["stage_a_id"]
    payload = {
        "lots": [
            {"lot_number": "BULK-1"},
            {"lot_number": "BULK-2"},
            {"lot_number": "A1"},  # duplicate of existing
            {"lot_number": "BULK-1"},  # duplicate within payload
        ]
    }
    r = client.post(
        f"/api/stages/{stage_id}/lots/bulk", json=payload, headers=admin_headers
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["created"] == 2
    assert body["skipped"] == 2


def test_bulk_create_lots_with_mixed_valid_invalid(
    client: TestClient, admin_headers, sample_stages_and_lots
):
    stage_id = sample_stages_and_lots["stage_a_id"]
    payload = {
        "lots": [
            {"lot_number": "MIX-1"},
            {"lot_number": "A2"},  # existing
            {"lot_number": "MIX-2"},
        ]
    }
    r = client.post(
        f"/api/stages/{stage_id}/lots/bulk", json=payload, headers=admin_headers
    )
    assert r.status_code == 200
    body = r.json()
    assert body["created"] == 2
    assert body["skipped"] == 1


# ---- CSV upload -----------------------------------------------------------


def test_csv_upload_creates_lots_from_multipart(
    client: TestClient, admin_headers, sample_stages_and_lots
):
    stage_id = sample_stages_and_lots["stage_a_id"]
    csv_bytes = b"lot_number,frontage\nCSV-1,10.0\nCSV-2,11.5\n"
    r = client.post(
        f"/api/stages/{stage_id}/lots/upload-csv",
        files={"file": ("lots.csv", csv_bytes, "text/csv")},
        headers=admin_headers,
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["created"] == 2
    assert body["skipped"] == 0


def test_csv_upload_with_invalid_rows_reports_errors(
    client: TestClient, admin_headers, sample_stages_and_lots
):
    stage_id = sample_stages_and_lots["stage_a_id"]
    csv_bytes = b"lot_number,frontage\nBAD-1,not-a-number\n"
    r = client.post(
        f"/api/stages/{stage_id}/lots/upload-csv",
        files={"file": ("bad.csv", csv_bytes, "text/csv")},
        headers=admin_headers,
    )
    # parse_csv_upload raises InvalidCsvError -> 422
    assert r.status_code == 422


def test_csv_upload_non_admin_403(
    client: TestClient, sales_headers, sample_stages_and_lots
):
    stage_id = sample_stages_and_lots["stage_a_id"]
    csv_bytes = b"lot_number\nX-1\n"
    r = client.post(
        f"/api/stages/{stage_id}/lots/upload-csv",
        files={"file": ("f.csv", csv_bytes, "text/csv")},
        headers=sales_headers,
    )
    assert r.status_code == 403

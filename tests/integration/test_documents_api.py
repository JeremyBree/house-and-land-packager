"""Integration tests: document upload/list/download/delete."""
from __future__ import annotations

from unittest.mock import patch

from fastapi.testclient import TestClient

from tests.integration.conftest import upload_file


PDF_BYTES = b"%PDF-1.4 small doc contents\n"


# ---- upload ---------------------------------------------------------------


def test_admin_uploads_document_201(
    client: TestClient, admin_headers, sample_data, tmp_storage
):
    estate_id = sample_data["estates"][0]["estate_id"]
    r = upload_file(
        client, estate_id, "spec.pdf", "application/pdf", PDF_BYTES,
        headers=admin_headers,
    )
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["file_name"] == "spec.pdf"
    assert body["file_type"] == "PDF"
    assert body["file_size"] == len(PDF_BYTES)
    assert body["estate_id"] == estate_id
    assert body["download_url"].startswith("/api/files/estate-documents/")


def test_upload_supports_stage_id_query_param(
    client: TestClient, admin_headers, sample_stages_and_lots, tmp_storage
):
    estate_id = sample_stages_and_lots["estate_id"]
    stage_id = sample_stages_and_lots["stage_a_id"]
    r = upload_file(
        client, estate_id, "stage.pdf", "application/pdf", PDF_BYTES,
        headers=admin_headers, stage_id=stage_id,
    )
    assert r.status_code == 201, r.text
    assert r.json()["stage_id"] == stage_id


def test_upload_supports_description_query_param(
    client: TestClient, admin_headers, sample_data, tmp_storage
):
    estate_id = sample_data["estates"][0]["estate_id"]
    r = upload_file(
        client, estate_id, "x.pdf", "application/pdf", PDF_BYTES,
        headers=admin_headers, description="brochure",
    )
    assert r.status_code == 201
    assert r.json()["description"] == "brochure"


def test_upload_invalid_file_type_415(
    client: TestClient, admin_headers, sample_data, tmp_storage
):
    estate_id = sample_data["estates"][0]["estate_id"]
    r = upload_file(
        client, estate_id, "malware.exe", "application/x-msdownload", b"MZ...",
        headers=admin_headers,
    )
    assert r.status_code == 415


def test_upload_oversized_file_413(
    client: TestClient, admin_headers, sample_data, tmp_storage
):
    estate_id = sample_data["estates"][0]["estate_id"]
    # Just over 10MB
    too_big = b"x" * (10 * 1024 * 1024 + 1)
    r = upload_file(
        client, estate_id, "big.pdf", "application/pdf", too_big,
        headers=admin_headers,
    )
    assert r.status_code == 413


def test_upload_non_admin_403(
    client: TestClient, sales_headers, sample_data, tmp_storage
):
    estate_id = sample_data["estates"][0]["estate_id"]
    r = upload_file(
        client, estate_id, "x.pdf", "application/pdf", PDF_BYTES,
        headers=sales_headers,
    )
    assert r.status_code == 403


# ---- list -----------------------------------------------------------------


def test_list_estate_documents_any_auth(
    client: TestClient, admin_headers, sales_headers, sample_data, tmp_storage
):
    estate_id = sample_data["estates"][0]["estate_id"]
    upload_file(
        client, estate_id, "a.pdf", "application/pdf", PDF_BYTES,
        headers=admin_headers,
    )
    upload_file(
        client, estate_id, "b.pdf", "application/pdf", PDF_BYTES,
        headers=admin_headers,
    )
    r = client.get(f"/api/estates/{estate_id}/documents", headers=sales_headers)
    assert r.status_code == 200
    assert len(r.json()) == 2


def test_list_documents_empty_estate(
    client: TestClient, admin_headers, sample_data, tmp_storage
):
    estate_id = sample_data["estates"][1]["estate_id"]
    r = client.get(f"/api/estates/{estate_id}/documents", headers=admin_headers)
    assert r.status_code == 200
    assert r.json() == []


# ---- download -------------------------------------------------------------


def test_download_document_returns_bytes_with_content_type(
    client: TestClient, admin_headers, sample_data, tmp_storage
):
    estate_id = sample_data["estates"][0]["estate_id"]
    up = upload_file(
        client, estate_id, "doc.pdf", "application/pdf", PDF_BYTES,
        headers=admin_headers,
    )
    doc_id = up.json()["document_id"]
    r = client.get(f"/api/documents/{doc_id}", headers=admin_headers)
    assert r.status_code == 200
    assert r.content == PDF_BYTES
    assert r.headers["content-type"].startswith("application/pdf")


def test_download_missing_document_404(
    client: TestClient, admin_headers, seeded_users, tmp_storage
):
    r = client.get("/api/documents/999999", headers=admin_headers)
    assert r.status_code == 404


# ---- delete ---------------------------------------------------------------


def test_admin_deletes_document_204(
    client: TestClient, admin_headers, sample_data, tmp_storage
):
    estate_id = sample_data["estates"][0]["estate_id"]
    up = upload_file(
        client, estate_id, "del.pdf", "application/pdf", PDF_BYTES,
        headers=admin_headers,
    )
    doc_id = up.json()["document_id"]
    r = client.delete(f"/api/documents/{doc_id}", headers=admin_headers)
    assert r.status_code == 204
    # Subsequent download returns 404
    r2 = client.get(f"/api/documents/{doc_id}", headers=admin_headers)
    assert r2.status_code == 404


def test_delete_document_removes_file_from_storage(
    client: TestClient, admin_headers, sample_data, tmp_storage
):
    estate_id = sample_data["estates"][0]["estate_id"]
    up = upload_file(
        client, estate_id, "removeme.pdf", "application/pdf", PDF_BYTES,
        headers=admin_headers,
    )
    doc_id = up.json()["document_id"]

    from hlp.shared import storage_service as ss

    with patch.object(
        ss._default_service,
        "delete_file",
        wraps=ss._default_service.delete_file,
    ) as mock_delete:
        r = client.delete(f"/api/documents/{doc_id}", headers=admin_headers)
        assert r.status_code == 204
        assert mock_delete.called


def test_delete_non_admin_403(
    client: TestClient, admin_headers, sales_headers, sample_data, tmp_storage
):
    estate_id = sample_data["estates"][0]["estate_id"]
    up = upload_file(
        client, estate_id, "keep.pdf", "application/pdf", PDF_BYTES,
        headers=admin_headers,
    )
    doc_id = up.json()["document_id"]
    r = client.delete(f"/api/documents/{doc_id}", headers=sales_headers)
    assert r.status_code == 403

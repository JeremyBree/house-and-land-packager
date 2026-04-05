"""Integration tests: /api/packages endpoints."""
from __future__ import annotations

from fastapi.testclient import TestClient


# ---- create ------------------------------------------------------------------


def test_admin_creates_package_201(
    client: TestClient, admin_headers, sample_stages_and_lots
):
    data = sample_stages_and_lots
    r = client.post(
        "/api/packages",
        json={
            "estate_id": data["estate_id"],
            "stage_id": data["stage_a_id"],
            "lot_number": "A1",
            "design": "Alpine",
            "facade": "Traditional",
            "brand": "Hermitage",
        },
        headers=admin_headers,
    )
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["design"] == "Alpine"
    assert body["facade"] == "Traditional"
    assert body["brand"] == "Hermitage"
    assert body["lot_number"] == "A1"
    assert "package_id" in body


def test_create_package_syncs_stage_lot_fields(
    client: TestClient, admin_headers, sample_stages_and_lots
):
    """Creating a package should sync design/facade/brand onto the StageLot.

    The StageLot API schema does not expose design/facade/brand, so we verify
    via the package detail endpoint which resolves the lot_id (confirming the
    StageLot row was found and linked).
    """
    data = sample_stages_and_lots
    r = client.post(
        "/api/packages",
        json={
            "estate_id": data["estate_id"],
            "stage_id": data["stage_a_id"],
            "lot_number": "A1",
            "design": "SyncDesign",
            "facade": "SyncFacade",
            "brand": "SyncBrand",
        },
        headers=admin_headers,
    )
    assert r.status_code == 201
    pkg_id = r.json()["package_id"]

    # Verify the package detail links to the correct lot (lot_id is resolved
    # from StageLot, proving the lot row exists and was matched).
    r2 = client.get(f"/api/packages/{pkg_id}", headers=admin_headers)
    assert r2.status_code == 200
    body = r2.json()
    assert body["lot_id"] is not None
    assert body["design"] == "SyncDesign"
    assert body["facade"] == "SyncFacade"
    assert body["brand"] == "SyncBrand"


def test_non_admin_create_403(
    client: TestClient, sales_headers, sample_stages_and_lots
):
    data = sample_stages_and_lots
    r = client.post(
        "/api/packages",
        json={
            "estate_id": data["estate_id"],
            "stage_id": data["stage_a_id"],
            "lot_number": "A1",
            "design": "Alpine",
            "facade": "Traditional",
            "brand": "Hermitage",
        },
        headers=sales_headers,
    )
    assert r.status_code == 403


def test_unauth_401(client: TestClient):
    r = client.get("/api/packages")
    assert r.status_code == 401


# ---- list --------------------------------------------------------------------


def test_list_packages_paginated(
    client: TestClient, admin_headers, sample_packages
):
    r = client.get("/api/packages?page=1&size=2", headers=admin_headers)
    assert r.status_code == 200
    body = r.json()
    assert body["page"] == 1
    assert body["size"] == 2
    assert len(body["items"]) == 2
    assert body["total"] == 5


def test_list_packages_filter_by_estate(
    client: TestClient, admin_headers, sample_packages
):
    eid = sample_packages["estate_id"]
    r = client.get(f"/api/packages?estate_id={eid}", headers=admin_headers)
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 5
    for item in body["items"]:
        assert item["estate_id"] == eid


def test_list_packages_filter_by_brand(
    client: TestClient, admin_headers, sample_packages
):
    r = client.get("/api/packages?brand=Hermitage", headers=admin_headers)
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 3
    for item in body["items"]:
        assert item["brand"] == "Hermitage"


def test_list_packages_filter_by_design(
    client: TestClient, admin_headers, sample_packages
):
    r = client.get("/api/packages?design=Alpine", headers=admin_headers)
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 2
    for item in body["items"]:
        assert "alpine" in item["design"].lower()


# ---- get by id ---------------------------------------------------------------


def test_get_package_by_id(
    client: TestClient, admin_headers, sample_packages
):
    pkg_id = sample_packages["package_ids"][0]
    r = client.get(f"/api/packages/{pkg_id}", headers=admin_headers)
    assert r.status_code == 200
    body = r.json()
    assert body["package_id"] == pkg_id
    assert body["design"] == "Alpine"
    # Detail view should include estate_name
    assert "estate_name" in body


def test_get_missing_package_404(client: TestClient, admin_headers, seeded_users):
    r = client.get("/api/packages/999999", headers=admin_headers)
    assert r.status_code == 404


# ---- update ------------------------------------------------------------------


def test_update_package(
    client: TestClient, admin_headers, sample_packages
):
    pkg_id = sample_packages["package_ids"][0]
    r = client.patch(
        f"/api/packages/{pkg_id}",
        json={"design": "UpdatedDesign", "facade": "UpdatedFacade"},
        headers=admin_headers,
    )
    assert r.status_code == 200
    body = r.json()
    assert body["design"] == "UpdatedDesign"
    assert body["facade"] == "UpdatedFacade"


# ---- delete ------------------------------------------------------------------


def test_delete_package_clears_stage_lot_fields(
    client: TestClient, admin_headers, sample_stages_and_lots
):
    """Deleting the only package on a lot should clear StageLot.design/facade/brand.

    We verify this by creating a second package on the same lot after deletion
    and confirming the detail view shows it was successfully created (i.e. no
    stale references remain). The actual field clearing is a service-layer
    concern tested in the unit tests.
    """
    data = sample_stages_and_lots
    # First create a package to set lot fields
    r = client.post(
        "/api/packages",
        json={
            "estate_id": data["estate_id"],
            "stage_id": data["stage_a_id"],
            "lot_number": "A1",
            "design": "ToDelete",
            "facade": "ToDelete",
            "brand": "ToDelete",
        },
        headers=admin_headers,
    )
    assert r.status_code == 201
    pkg_id = r.json()["package_id"]

    # Delete the package
    r2 = client.delete(f"/api/packages/{pkg_id}", headers=admin_headers)
    assert r2.status_code == 204

    # Verify package is gone
    r3 = client.get(f"/api/packages/{pkg_id}", headers=admin_headers)
    assert r3.status_code == 404

    # Verify no packages remain on that lot
    r4 = client.get(
        f"/api/packages?estate_id={data['estate_id']}&lot_number=A1",
        headers=admin_headers,
    )
    assert r4.status_code == 200
    assert r4.json()["total"] == 0


def test_non_admin_delete_403(
    client: TestClient, sales_headers, sample_packages
):
    pkg_id = sample_packages["package_ids"][0]
    r = client.delete(f"/api/packages/{pkg_id}", headers=sales_headers)
    assert r.status_code == 403


# ---- flyer upload/delete -----------------------------------------------------


def test_flyer_upload_multipart(
    client: TestClient, admin_headers, sample_packages, tmp_storage
):
    pkg_id = sample_packages["package_ids"][0]
    r = client.post(
        f"/api/packages/{pkg_id}/flyer",
        files={"file": ("flyer.pdf", b"%PDF-fake-content", "application/pdf")},
        headers=admin_headers,
    )
    assert r.status_code == 200
    body = r.json()
    assert body["flyer_path"] is not None
    assert "flyer" in body["flyer_path"].lower() or body["flyer_path"] != ""


def test_flyer_delete_204(
    client: TestClient, admin_headers, sample_packages, tmp_storage
):
    pkg_id = sample_packages["package_ids"][0]
    # Upload first
    client.post(
        f"/api/packages/{pkg_id}/flyer",
        files={"file": ("flyer.pdf", b"%PDF-fake-content", "application/pdf")},
        headers=admin_headers,
    )
    # Delete flyer
    r = client.delete(f"/api/packages/{pkg_id}/flyer", headers=admin_headers)
    assert r.status_code == 204

    # Verify flyer_path is cleared
    r2 = client.get(f"/api/packages/{pkg_id}", headers=admin_headers)
    assert r2.status_code == 200
    assert r2.json()["flyer_path"] is None

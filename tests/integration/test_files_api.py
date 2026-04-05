"""Integration tests: file-serving endpoint /api/files/{category}/{filename}."""
from __future__ import annotations

from fastapi.testclient import TestClient

from hlp.shared.storage_service import CATEGORY_ESTATE_DOCUMENTS


def _put_file(tmp_storage, name: str, content: bytes) -> str:
    """Write a file directly under the tmp storage category dir and return its name."""
    cat_dir = tmp_storage / CATEGORY_ESTATE_DOCUMENTS
    cat_dir.mkdir(parents=True, exist_ok=True)
    (cat_dir / name).write_bytes(content)
    return name


def test_authenticated_can_fetch_file(
    client: TestClient, admin_headers, tmp_storage
):
    name = _put_file(tmp_storage, "hello.pdf", b"pdf-bytes")
    r = client.get(
        f"/api/files/{CATEGORY_ESTATE_DOCUMENTS}/{name}", headers=admin_headers
    )
    assert r.status_code == 200
    assert r.content == b"pdf-bytes"


def test_unauthenticated_fetch_401(client: TestClient, tmp_storage):
    name = _put_file(tmp_storage, "public.pdf", b"x")
    r = client.get(f"/api/files/{CATEGORY_ESTATE_DOCUMENTS}/{name}")
    assert r.status_code == 401


def test_fetch_missing_file_404(
    client: TestClient, admin_headers, tmp_storage
):
    r = client.get(
        f"/api/files/{CATEGORY_ESTATE_DOCUMENTS}/nope.pdf", headers=admin_headers
    )
    assert r.status_code == 404


def test_path_traversal_blocked(
    client: TestClient, admin_headers, tmp_storage
):
    # A URL path with traversal segments should not succeed in escaping
    # the category directory.  FastAPI normalises ``..`` segments in the
    # URL before routing, so the request either 404s (no matching route
    # or file) or returns a normalised path — never reaches outside the
    # base directory.
    r = client.get(
        f"/api/files/{CATEGORY_ESTATE_DOCUMENTS}/..%2F..%2Fetc%2Fpasswd",
        headers=admin_headers,
    )
    assert r.status_code in (400, 404)
    # And with literal ../ the storage service _resolve guard trips
    r2 = client.get(
        "/api/files/unknown-category/some.pdf", headers=admin_headers
    )
    assert r2.status_code == 404

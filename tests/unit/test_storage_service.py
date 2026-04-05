"""Unit tests for StorageService (Railway Volume wrapper)."""
from __future__ import annotations

import pytest

from hlp.shared.storage_service import (
    CATEGORY_ESTATE_DOCUMENTS,
    StorageService,
)


def test_save_and_read_roundtrip(tmp_path):
    svc = StorageService(base_path=str(tmp_path))
    stored_path, size = svc.save_file(
        CATEGORY_ESTATE_DOCUMENTS, "hello.pdf", b"hello world"
    )
    assert size == len(b"hello world")
    assert svc.read_file(stored_path) == b"hello world"


def test_save_file_returns_size(tmp_path):
    svc = StorageService(base_path=str(tmp_path))
    content = b"x" * 4096
    _, size = svc.save_file(CATEGORY_ESTATE_DOCUMENTS, "big.pdf", content)
    assert size == 4096


def test_save_file_sanitizes_filename(tmp_path):
    svc = StorageService(base_path=str(tmp_path))
    stored_path, _ = svc.save_file(
        CATEGORY_ESTATE_DOCUMENTS, "../../etc/passwd.pdf", b"data"
    )
    # The sanitized name must not contain ".." and must keep the .pdf extension
    assert ".." not in stored_path
    assert stored_path.endswith(".pdf")
    # And the file is in the expected category dir
    assert stored_path.startswith(f"{CATEGORY_ESTATE_DOCUMENTS}/")
    # Reading back works
    assert svc.read_file(stored_path) == b"data"


def test_save_file_creates_category_dir(tmp_path):
    svc = StorageService(base_path=str(tmp_path))
    # Subdir doesn't exist yet
    assert not (tmp_path / CATEGORY_ESTATE_DOCUMENTS).exists()
    svc.save_file(CATEGORY_ESTATE_DOCUMENTS, "a.pdf", b"ok")
    assert (tmp_path / CATEGORY_ESTATE_DOCUMENTS).is_dir()


def test_delete_file_removes_from_disk(tmp_path):
    svc = StorageService(base_path=str(tmp_path))
    stored_path, _ = svc.save_file(
        CATEGORY_ESTATE_DOCUMENTS, "gone.pdf", b"bytes"
    )
    abs_path = svc.get_absolute_path(stored_path)
    assert abs_path.exists()
    svc.delete_file(stored_path)
    assert not abs_path.exists()


def test_delete_nonexistent_file_does_not_raise(tmp_path):
    svc = StorageService(base_path=str(tmp_path))
    # Should be idempotent / silent
    svc.delete_file(f"{CATEGORY_ESTATE_DOCUMENTS}/missing.pdf")


def test_read_nonexistent_file_raises(tmp_path):
    svc = StorageService(base_path=str(tmp_path))
    with pytest.raises(FileNotFoundError):
        svc.read_file(f"{CATEGORY_ESTATE_DOCUMENTS}/nope.pdf")


def test_get_download_url_format(tmp_path):
    svc = StorageService(base_path=str(tmp_path))
    url = svc.get_download_url(f"{CATEGORY_ESTATE_DOCUMENTS}/abc.pdf")
    assert url == f"/api/files/{CATEGORY_ESTATE_DOCUMENTS}/abc.pdf"

"""Railway Volume-backed file storage service.

Wraps the filesystem volume mounted at ``settings.storage_base_path``. Designed
for straightforward future migration to Azure Blob by swapping the backend.
"""

from __future__ import annotations

import re
from pathlib import Path, PurePosixPath
from uuid import uuid4

from hlp.config import get_settings

CATEGORY_ESTATE_DOCUMENTS = "estate-documents"
CATEGORY_PACKAGE_FLYERS = "package-flyers"
CATEGORY_GENERATED_SHEETS = "generated-sheets"

ALLOWED_CATEGORIES = {
    CATEGORY_ESTATE_DOCUMENTS,
    CATEGORY_PACKAGE_FLYERS,
    CATEGORY_GENERATED_SHEETS,
}

_SAFE_CHAR_RE = re.compile(r"[^A-Za-z0-9._-]+")


def _sanitize_filename(original_filename: str) -> str:
    """Strip paths and unsafe characters while preserving the extension."""
    # Strip any directory components (handle both separators)
    base = original_filename.replace("\\", "/").split("/")[-1]
    if not base:
        base = "file"
    # Split extension
    if "." in base:
        stem, _, ext = base.rpartition(".")
        ext = "." + _SAFE_CHAR_RE.sub("", ext).lower()
    else:
        stem, ext = base, ""
    stem = _SAFE_CHAR_RE.sub("_", stem).strip("_.") or "file"
    return f"{stem}{ext}"


class StorageService:
    """Thin wrapper over the Railway volume at ``storage_base_path``."""

    def __init__(self, base_path: str | None = None) -> None:
        self._base_path = Path(base_path or get_settings().storage_base_path)

    @property
    def base_path(self) -> Path:
        return self._base_path

    def _category_dir(self, category: str) -> Path:
        if category not in ALLOWED_CATEGORIES:
            raise ValueError(f"Unknown storage category: {category}")
        return self._base_path / category

    def save_file(
        self, category: str, original_filename: str, content: bytes
    ) -> tuple[str, int]:
        """Persist bytes under ``{category}/{uuid}_{safe_filename}``.

        Returns ``(stored_path, size_bytes)`` where ``stored_path`` uses
        forward slashes regardless of platform.
        """
        safe = _sanitize_filename(original_filename)
        directory = self._category_dir(category)
        directory.mkdir(parents=True, exist_ok=True)
        stored_name = f"{uuid4().hex}_{safe}"
        abs_path = directory / stored_name
        abs_path.write_bytes(content)
        rel_posix = str(PurePosixPath(category) / stored_name)
        return rel_posix, len(content)

    def _resolve(self, stored_path: str) -> Path:
        rel = PurePosixPath(stored_path)
        # Guard against path escape
        if rel.is_absolute() or ".." in rel.parts:
            raise ValueError(f"Invalid stored path: {stored_path}")
        return self._base_path.joinpath(*rel.parts)

    def read_file(self, stored_path: str) -> bytes:
        return self._resolve(stored_path).read_bytes()

    def delete_file(self, stored_path: str) -> None:
        path = self._resolve(stored_path)
        if path.exists():
            path.unlink()

    def get_download_url(self, stored_path: str) -> str:
        return f"/api/files/{stored_path}"

    def get_absolute_path(self, stored_path: str) -> Path:
        return self._resolve(stored_path)


_default_service: StorageService | None = None


def get_storage_service() -> StorageService:
    global _default_service
    if _default_service is None:
        _default_service = StorageService()
    return _default_service

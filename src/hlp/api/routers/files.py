"""File-serving router backed by the storage volume."""

import mimetypes

from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse

from hlp.api.deps import get_current_user
from hlp.shared.exceptions import NotFoundError
from hlp.shared.storage_service import ALLOWED_CATEGORIES, get_storage_service

router = APIRouter(prefix="/api/files", tags=["files"])


@router.get(
    "/{category}/{filename}",
    dependencies=[Depends(get_current_user)],
)
def serve_file(category: str, filename: str) -> FileResponse:
    if category not in ALLOWED_CATEGORIES:
        raise NotFoundError(f"Unknown file category: {category}")
    storage = get_storage_service()
    stored_path = f"{category}/{filename}"
    abs_path = storage.get_absolute_path(stored_path)
    if not abs_path.exists() or not abs_path.is_file():
        raise NotFoundError(f"File not found: {stored_path}")
    content_type, _ = mimetypes.guess_type(filename)
    if content_type is None:
        content_type = "application/octet-stream"
    return FileResponse(
        path=str(abs_path),
        media_type=content_type,
        filename=filename,
    )

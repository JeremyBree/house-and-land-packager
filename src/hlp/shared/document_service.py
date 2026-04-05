"""Estate document upload service."""

from __future__ import annotations

from sqlalchemy.orm import Session

from hlp.models.estate_document import EstateDocument
from hlp.repositories import document_repository
from hlp.shared.exceptions import FileTooLargeError, UnsupportedFileTypeError
from hlp.shared.storage_service import CATEGORY_ESTATE_DOCUMENTS, get_storage_service

MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB

# Map mime-type -> short type code stored in file_type column
_MIME_TYPE_MAP = {
    "application/pdf": "PDF",
    "application/msword": "DOC",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "DOCX",
    "image/png": "PNG",
    "image/jpeg": "JPG",
    "image/jpg": "JPG",
}

# Map filename extension -> short type code (fallback if mime is absent/wrong)
_EXT_MAP = {
    "pdf": "PDF",
    "doc": "DOC",
    "docx": "DOCX",
    "png": "PNG",
    "jpg": "JPG",
    "jpeg": "JPEG",
}


def _resolve_file_type(file_name: str, content_type: str | None) -> str:
    if content_type:
        code = _MIME_TYPE_MAP.get(content_type.lower())
        if code is not None:
            return code
    if "." in file_name:
        ext = file_name.rsplit(".", 1)[-1].lower()
        code = _EXT_MAP.get(ext)
        if code is not None:
            return code
    raise UnsupportedFileTypeError(
        f"File type not supported for '{file_name}' (content-type={content_type!r}). "
        "Allowed: PDF, DOC, DOCX, PNG, JPG, JPEG"
    )


def upload_estate_document(
    db: Session,
    estate_id: int,
    stage_id: int | None,
    file_name: str,
    content_type: str | None,
    content: bytes,
    description: str | None,
) -> EstateDocument:
    """Validate, persist to storage, and create an EstateDocument row."""
    if len(content) > MAX_FILE_SIZE_BYTES:
        raise FileTooLargeError(
            f"File '{file_name}' exceeds the 10 MB limit"
            f" ({len(content)} bytes)"
        )
    file_type = _resolve_file_type(file_name, content_type)

    storage = get_storage_service()
    stored_path, size_bytes = storage.save_file(
        CATEGORY_ESTATE_DOCUMENTS, file_name, content
    )
    doc = document_repository.create(
        db,
        estate_id=estate_id,
        stage_id=stage_id,
        file_name=file_name,
        file_type=file_type,
        file_size=size_bytes,
        file_path=stored_path,
        description=description,
    )
    return doc

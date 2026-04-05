"""Estate document router."""

import mimetypes
from typing import Annotated

from fastapi import APIRouter, Depends, File, Query, UploadFile, status
from fastapi.responses import Response
from sqlalchemy.orm import Session

from hlp.api.deps import get_current_user, get_db, require_admin
from hlp.api.schemas.document import DocumentRead
from hlp.repositories import document_repository, estate_repository, stage_repository
from hlp.shared import document_service
from hlp.shared.exceptions import (
    DocumentNotFoundError,
    NotFoundError,
    StageNotFoundError,
)
from hlp.shared.storage_service import get_storage_service

estate_scoped_router = APIRouter(prefix="/api/estates", tags=["documents"])
docs_router = APIRouter(prefix="/api/documents", tags=["documents"])


def _to_read(doc) -> DocumentRead:
    download_url = get_storage_service().get_download_url(doc.file_path)
    return DocumentRead(
        document_id=doc.document_id,
        estate_id=doc.estate_id,
        stage_id=doc.stage_id,
        file_name=doc.file_name,
        file_type=doc.file_type,
        file_size=doc.file_size,
        description=doc.description,
        created_at=doc.created_at,
        download_url=download_url,
    )


@estate_scoped_router.post(
    "/{estate_id}/documents",
    response_model=DocumentRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)],
)
async def upload_document(
    estate_id: int,
    db: Annotated[Session, Depends(get_db)],
    file: UploadFile = File(...),
    stage_id: int | None = Query(default=None),
    description: str | None = Query(default=None),
) -> DocumentRead:
    if estate_repository.get(db, estate_id) is None:
        raise NotFoundError(f"Estate {estate_id} not found")
    if stage_id is not None and stage_repository.get(db, stage_id) is None:
        raise StageNotFoundError(f"Stage {stage_id} not found")
    content = await file.read()
    doc = document_service.upload_estate_document(
        db,
        estate_id=estate_id,
        stage_id=stage_id,
        file_name=file.filename or "upload",
        content_type=file.content_type,
        content=content,
        description=description,
    )
    db.commit()
    db.refresh(doc)
    return _to_read(doc)


@estate_scoped_router.get(
    "/{estate_id}/documents",
    response_model=list[DocumentRead],
    dependencies=[Depends(get_current_user)],
)
def list_documents(
    estate_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> list[DocumentRead]:
    if estate_repository.get(db, estate_id) is None:
        raise NotFoundError(f"Estate {estate_id} not found")
    docs = document_repository.list_by_estate(db, estate_id)
    return [_to_read(d) for d in docs]


@docs_router.get(
    "/{document_id}",
    dependencies=[Depends(get_current_user)],
)
def download_document(
    document_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> Response:
    doc = document_repository.get(db, document_id)
    if doc is None:
        raise DocumentNotFoundError(f"Document {document_id} not found")
    storage = get_storage_service()
    content = storage.read_file(doc.file_path)
    content_type, _ = mimetypes.guess_type(doc.file_name)
    if content_type is None:
        content_type = "application/octet-stream"
    headers = {"Content-Disposition": f'attachment; filename="{doc.file_name}"'}
    return Response(content=content, media_type=content_type, headers=headers)


@docs_router.delete(
    "/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_admin)],
)
def delete_document(
    document_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> None:
    doc = document_repository.get(db, document_id)
    if doc is None:
        raise DocumentNotFoundError(f"Document {document_id} not found")
    storage = get_storage_service()
    try:
        storage.delete_file(doc.file_path)
    except Exception:
        # Don't block DB delete if file is already missing
        pass
    document_repository.delete(db, document_id)
    db.commit()

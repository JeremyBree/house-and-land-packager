"""PDF ingestion router — upload, extract, review, approve/reject."""

from typing import Annotated

from fastapi import APIRouter, Depends, File, Query, UploadFile, status
from sqlalchemy.orm import Session

from hlp.api.deps import get_current_user, get_db, require_admin
from hlp.api.schemas.pdf_ingestion_schema import (
    ApproveInput,
    PendingExtractionRead,
    RejectInput,
)
from hlp.models.profile import Profile
from hlp.repositories import pending_extraction_repository
from hlp.shared import pdf_ingestion_service
from hlp.shared.exceptions import NotFoundError

router = APIRouter(prefix="/api/pdf-ingestion", tags=["pdf-ingestion"])


@router.post(
    "/upload",
    response_model=PendingExtractionRead,
    status_code=status.HTTP_201_CREATED,
)
async def upload_pdf(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: Profile = Depends(get_current_user),
) -> PendingExtractionRead:
    """Upload a developer price list PDF for AI extraction."""
    content = await file.read()
    record = pdf_ingestion_service.upload_and_extract(
        db=db,
        file_name=file.filename or "upload.pdf",
        content_type=file.content_type or "application/pdf",
        content=content,
        uploaded_by=current_user.profile_id,
    )
    return PendingExtractionRead.model_validate(record)


@router.get(
    "/extractions",
    response_model=list[PendingExtractionRead],
    dependencies=[Depends(get_current_user)],
)
def list_extractions(
    db: Annotated[Session, Depends(get_db)],
    status_filter: str | None = Query(default=None, alias="status"),
) -> list[PendingExtractionRead]:
    """List pending extractions, optionally filtered by status."""
    rows = pending_extraction_repository.list_pending(db, status=status_filter)
    return [PendingExtractionRead.model_validate(r) for r in rows]


@router.get(
    "/extractions/{extraction_id}",
    response_model=PendingExtractionRead,
    dependencies=[Depends(get_current_user)],
)
def get_extraction(
    extraction_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> PendingExtractionRead:
    """Get a single extraction with its extracted data."""
    record = pending_extraction_repository.get(db, extraction_id)
    if record is None:
        raise NotFoundError(f"PendingExtraction {extraction_id} not found")
    return PendingExtractionRead.model_validate(record)


@router.post(
    "/extractions/{extraction_id}/approve",
    response_model=PendingExtractionRead,
    dependencies=[Depends(require_admin)],
)
def approve_extraction(
    extraction_id: int,
    payload: ApproveInput,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Profile, Depends(get_current_user)],
) -> PendingExtractionRead:
    """Approve a pending extraction and commit data to the database."""
    record = pdf_ingestion_service.approve_extraction(
        db=db,
        extraction_id=extraction_id,
        reviewed_by=current_user.profile_id,
        review_notes=payload.review_notes,
    )
    return PendingExtractionRead.model_validate(record)


@router.post(
    "/extractions/{extraction_id}/reject",
    response_model=PendingExtractionRead,
    dependencies=[Depends(require_admin)],
)
def reject_extraction(
    extraction_id: int,
    payload: RejectInput,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Profile, Depends(get_current_user)],
) -> PendingExtractionRead:
    """Reject a pending extraction."""
    record = pdf_ingestion_service.reject_extraction(
        db=db,
        extraction_id=extraction_id,
        reviewed_by=current_user.profile_id,
        review_notes=payload.review_notes,
    )
    return PendingExtractionRead.model_validate(record)


@router.delete(
    "/extractions/{extraction_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_admin)],
)
def delete_extraction(
    extraction_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> None:
    """Delete a pending extraction record."""
    pending_extraction_repository.delete(db, extraction_id)
    db.commit()

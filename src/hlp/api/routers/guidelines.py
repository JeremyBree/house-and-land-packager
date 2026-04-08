"""Guideline types & estate design guidelines router."""

from typing import Annotated

from fastapi import APIRouter, Depends, File, Query, UploadFile, status
from sqlalchemy.orm import Session

from hlp.api.deps import get_current_user, get_db, require_admin
from hlp.api.schemas.guideline_schema import (
    EstateGuidelineCreate,
    EstateGuidelineRead,
    EstateGuidelineUpdate,
    GuidelineCopyRequest,
    GuidelineTypeCreate,
    GuidelineTypeRead,
    GuidelineTypeUpdate,
)
from hlp.api.schemas.common import CsvRowError, CsvUploadResult
from hlp.repositories import guideline_repository
from hlp.shared import csv_import_service
from hlp.shared.exceptions import NotFoundError

router = APIRouter(prefix="/api/guidelines", tags=["guidelines"])


# ---- Guideline Types ---------------------------------------------------------

@router.get(
    "/types",
    response_model=list[GuidelineTypeRead],
    dependencies=[Depends(get_current_user)],
)
def list_guideline_types(
    db: Annotated[Session, Depends(get_db)],
) -> list[GuidelineTypeRead]:
    rows = guideline_repository.list_guideline_types(db)
    return [GuidelineTypeRead.model_validate(r) for r in rows]


@router.post(
    "/types",
    response_model=GuidelineTypeRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)],
)
def create_guideline_type(
    payload: GuidelineTypeCreate,
    db: Annotated[Session, Depends(get_db)],
) -> GuidelineTypeRead:
    obj = guideline_repository.create_guideline_type(db, **payload.model_dump())
    db.commit()
    db.refresh(obj)
    return GuidelineTypeRead.model_validate(obj)


@router.patch(
    "/types/{type_id}",
    response_model=GuidelineTypeRead,
    dependencies=[Depends(require_admin)],
)
def update_guideline_type(
    type_id: int,
    payload: GuidelineTypeUpdate,
    db: Annotated[Session, Depends(get_db)],
) -> GuidelineTypeRead:
    obj = guideline_repository.update_guideline_type(db, type_id, **payload.model_dump(exclude_unset=True))
    db.commit()
    db.refresh(obj)
    return GuidelineTypeRead.model_validate(obj)


@router.delete(
    "/types/{type_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_admin)],
)
def delete_guideline_type(
    type_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> None:
    existing = guideline_repository.get_guideline_type(db, type_id)
    if existing is None:
        raise NotFoundError(f"GuidelineType {type_id} not found")
    guideline_repository.delete_guideline_type(db, type_id)
    db.commit()


# ---- Estate Design Guidelines ------------------------------------------------

def _guideline_to_read(g) -> EstateGuidelineRead:
    d = {c.key: getattr(g, c.key) for c in g.__table__.columns}
    d["guideline_type_name"] = g.guideline_type.short_name if g.guideline_type else None
    d["default_price"] = float(g.guideline_type.default_price) if g.guideline_type and g.guideline_type.default_price else None
    d["category_description"] = g.guideline_type.category_name if g.guideline_type else None
    return EstateGuidelineRead.model_validate(d)


@router.get(
    "/estate",
    response_model=list[EstateGuidelineRead],
    dependencies=[Depends(get_current_user)],
)
def list_estate_guidelines(
    db: Annotated[Session, Depends(get_db)],
    estate_id: int = Query(),
    stage_id: int | None = Query(default=None),
) -> list[EstateGuidelineRead]:
    rows = guideline_repository.list_estate_guidelines(db, estate_id=estate_id, stage_id=stage_id)
    return [_guideline_to_read(r) for r in rows]


@router.post(
    "/estate",
    response_model=EstateGuidelineRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)],
)
def create_estate_guideline(
    payload: EstateGuidelineCreate,
    db: Annotated[Session, Depends(get_db)],
) -> EstateGuidelineRead:
    obj = guideline_repository.create_estate_guideline(db, **payload.model_dump())
    db.commit()
    db.refresh(obj)
    return _guideline_to_read(obj)


@router.post("/estate/copy", dependencies=[Depends(require_admin)])
def copy_estate_guidelines(
    payload: GuidelineCopyRequest,
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    count = guideline_repository.copy_guidelines(
        db, payload.source_estate_id, payload.source_stage_id,
        payload.target_estate_id, payload.target_stage_id,
    )
    db.commit()
    return {"copied": count}


@router.patch(
    "/estate/{guideline_id}",
    response_model=EstateGuidelineRead,
    dependencies=[Depends(require_admin)],
)
def update_estate_guideline(
    guideline_id: int,
    payload: EstateGuidelineUpdate,
    db: Annotated[Session, Depends(get_db)],
) -> EstateGuidelineRead:
    obj = guideline_repository.update_estate_guideline(db, guideline_id, **payload.model_dump(exclude_unset=True))
    db.commit()
    db.refresh(obj)
    return _guideline_to_read(obj)


@router.delete(
    "/estate/{guideline_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_admin)],
)
def delete_estate_guideline(
    guideline_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> None:
    existing = guideline_repository.get_estate_guideline(db, guideline_id)
    if existing is None:
        raise NotFoundError(f"EstateDesignGuideline {guideline_id} not found")
    guideline_repository.delete_estate_guideline(db, guideline_id)
    db.commit()


# ---- CSV Uploads -------------------------------------------------------------


@router.post(
    "/types/upload-csv",
    response_model=CsvUploadResult,
    dependencies=[Depends(require_admin)],
)
async def upload_guideline_types_csv(
    db: Annotated[Session, Depends(get_db)],
    file: UploadFile = File(...),
) -> CsvUploadResult:
    content = await file.read()
    parsed = csv_import_service.parse_guideline_types_csv(content)
    created, skipped, errors = csv_import_service.bulk_create_guideline_types(db, parsed)
    db.commit()
    return CsvUploadResult(created=created, skipped=skipped, errors=[CsvRowError(**e) for e in errors])


@router.post(
    "/estate/upload-csv",
    response_model=CsvUploadResult,
    dependencies=[Depends(require_admin)],
)
async def upload_estate_guidelines_csv(
    db: Annotated[Session, Depends(get_db)],
    file: UploadFile = File(...),
) -> CsvUploadResult:
    content = await file.read()
    parsed = csv_import_service.parse_estate_guidelines_csv(content)
    created, skipped, errors = csv_import_service.bulk_create_estate_guidelines(db, parsed)
    db.commit()
    return CsvUploadResult(created=created, skipped=skipped, errors=[CsvRowError(**e) for e in errors])

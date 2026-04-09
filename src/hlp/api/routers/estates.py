"""Estate router."""

import math
from typing import Annotated

from fastapi import APIRouter, Depends, File, Query, UploadFile, status
from sqlalchemy.orm import Session

from hlp.api.deps import get_current_user, get_db, require_admin
from hlp.api.schemas.common import PaginatedResponse
from hlp.api.schemas.estate import (
    EstateCreate,
    EstateDetailRead,
    EstateRead,
    EstateUpdate,
)
from hlp.repositories import estate_repository
from hlp.shared import csv_import_service
from hlp.shared.exceptions import NotFoundError

router = APIRouter(prefix="/api/estates", tags=["estates"])


@router.get(
    "",
    response_model=PaginatedResponse[EstateRead],
    dependencies=[Depends(get_current_user)],
)
def list_estates(
    db: Annotated[Session, Depends(get_db)],
    page: int = Query(1, ge=1),
    size: int = Query(25, ge=1, le=200),
    search: str | None = None,
    developer_id: int | None = None,
    region_id: int | None = None,
    active: bool | None = None,
) -> PaginatedResponse[EstateRead]:
    items, total = estate_repository.list_paginated(
        db,
        page=page,
        size=size,
        search=search,
        developer_id=developer_id,
        region_id=region_id,
        active=active,
    )
    pages = math.ceil(total / size) if size else 0
    return PaginatedResponse[EstateRead](
        items=[EstateRead.model_validate(e) for e in items],
        total=total,
        page=page,
        size=size,
        pages=pages,
    )


# ---- CSV Upload (must be before /{estate_id} routes) -------------------------


@router.post(
    "/upload-csv",
    dependencies=[Depends(require_admin)],
)
async def upload_estates_stages_csv(
    db: Annotated[Session, Depends(get_db)],
    file: UploadFile = File(...),
) -> dict:
    content = await file.read()
    parsed = csv_import_service.parse_estates_stages_csv(content)
    estates_created, stages_created, skipped, errors = (
        csv_import_service.bulk_create_estates_stages(db, parsed)
    )
    db.commit()
    return {
        "estates_created": estates_created,
        "stages_created": stages_created,
        "skipped": skipped,
        "errors": [{"row": e["row"], "error": e["error"]} for e in errors[:50]],
    }


# ---- CRUD ---------------------------------------------------------------------


@router.get(
    "/{estate_id}",
    response_model=EstateDetailRead,
    dependencies=[Depends(get_current_user)],
)
def get_estate(
    estate_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> EstateDetailRead:
    estate = estate_repository.get_with_relations(db, estate_id)
    if estate is None:
        raise NotFoundError(f"Estate {estate_id} not found")
    stages_count = estate_repository.count_stages(db, estate_id)
    return EstateDetailRead.model_validate(
        {**estate.__dict__, "developer": estate.developer, "region": estate.region, "stages_count": stages_count}
    )


@router.post(
    "",
    response_model=EstateDetailRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)],
)
def create_estate(
    payload: EstateCreate,
    db: Annotated[Session, Depends(get_db)],
) -> EstateDetailRead:
    fields = payload.model_dump()
    if fields.get("contact_email") is not None:
        fields["contact_email"] = str(fields["contact_email"])
    estate = estate_repository.create(db, **fields)
    db.commit()
    estate = estate_repository.get_with_relations(db, estate.estate_id)
    assert estate is not None
    return EstateDetailRead.model_validate(estate)


@router.patch(
    "/{estate_id}",
    response_model=EstateDetailRead,
    dependencies=[Depends(require_admin)],
)
def update_estate(
    estate_id: int,
    payload: EstateUpdate,
    db: Annotated[Session, Depends(get_db)],
) -> EstateDetailRead:
    fields = payload.model_dump(exclude_unset=True)
    if fields.get("contact_email") is not None:
        fields["contact_email"] = str(fields["contact_email"])
    estate_repository.update(db, estate_id, **fields)
    db.commit()
    estate = estate_repository.get_with_relations(db, estate_id)
    assert estate is not None
    return EstateDetailRead.model_validate(estate)


@router.delete(
    "/{estate_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_admin)],
)
def delete_estate(
    estate_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> None:
    estate_repository.soft_delete(db, estate_id)
    db.commit()

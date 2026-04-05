"""Stage lot router."""

import math
from typing import Annotated

from fastapi import APIRouter, Depends, File, Query, UploadFile, status
from sqlalchemy.orm import Session

from hlp.api.deps import get_current_user, get_db, require_admin, require_roles
from hlp.api.schemas.common import PaginatedResponse
from hlp.api.schemas.lot import (
    CsvRowError,
    CsvUploadResult,
    LotBulkCreate,
    LotCreate,
    LotRead,
    LotStatusTransition,
    LotUpdate,
    StatusHistoryRead,
)
from hlp.models.enums import LotStatus, Source, UserRoleType
from hlp.models.profile import Profile
from hlp.repositories import (
    lot_repository,
    stage_repository,
    status_history_repository,
)
from hlp.shared import lot_service
from hlp.shared.exceptions import LotNotFoundError, StageNotFoundError

stages_scoped_router = APIRouter(prefix="/api/stages", tags=["lots"])
lots_router = APIRouter(prefix="/api/lots", tags=["lots"])


def _ensure_stage(db: Session, stage_id: int) -> None:
    if stage_repository.get(db, stage_id) is None:
        raise StageNotFoundError(f"Stage {stage_id} not found")


@stages_scoped_router.get(
    "/{stage_id}/lots",
    response_model=PaginatedResponse[LotRead],
    dependencies=[Depends(get_current_user)],
)
def list_lots(
    stage_id: int,
    db: Annotated[Session, Depends(get_db)],
    page: int = Query(1, ge=1),
    size: int = Query(25, ge=1, le=200),
    status: LotStatus | None = Query(default=None),
) -> PaginatedResponse[LotRead]:
    _ensure_stage(db, stage_id)
    items, total = lot_repository.list_by_stage_paginated(
        db, stage_id=stage_id, page=page, size=size, status=status
    )
    pages = math.ceil(total / size) if size else 0
    return PaginatedResponse[LotRead](
        items=[LotRead.model_validate(lot) for lot in items],
        total=total,
        page=page,
        size=size,
        pages=pages,
    )


@stages_scoped_router.post(
    "/{stage_id}/lots",
    response_model=LotRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)],
)
def create_lot(
    stage_id: int,
    payload: LotCreate,
    db: Annotated[Session, Depends(get_db)],
) -> LotRead:
    _ensure_stage(db, stage_id)
    lot = lot_repository.create(
        db, stage_id=stage_id, source=Source.MANUAL, **payload.model_dump()
    )
    db.commit()
    db.refresh(lot)
    return LotRead.model_validate(lot)


@stages_scoped_router.post(
    "/{stage_id}/lots/bulk",
    response_model=CsvUploadResult,
    dependencies=[Depends(require_admin)],
)
def bulk_create_lots(
    stage_id: int,
    payload: LotBulkCreate,
    db: Annotated[Session, Depends(get_db)],
) -> CsvUploadResult:
    _ensure_stage(db, stage_id)
    created, skipped, errors = lot_service.bulk_create_lots(db, stage_id, payload.lots)
    db.commit()
    return CsvUploadResult(
        created=created,
        skipped=skipped,
        errors=[CsvRowError(**e) for e in errors],
    )


@stages_scoped_router.post(
    "/{stage_id}/lots/upload-csv",
    response_model=CsvUploadResult,
    dependencies=[Depends(require_admin)],
)
async def upload_lots_csv(
    stage_id: int,
    db: Annotated[Session, Depends(get_db)],
    file: UploadFile = File(...),
) -> CsvUploadResult:
    _ensure_stage(db, stage_id)
    content = await file.read()
    parsed = lot_service.parse_csv_upload(content)
    created, skipped, errors = lot_service.bulk_create_lots(db, stage_id, parsed)
    db.commit()
    return CsvUploadResult(
        created=created,
        skipped=skipped,
        errors=[CsvRowError(**e) for e in errors],
    )


@lots_router.get(
    "/{lot_id}",
    response_model=LotRead,
    dependencies=[Depends(get_current_user)],
)
def get_lot(
    lot_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> LotRead:
    lot = lot_repository.get(db, lot_id)
    if lot is None:
        raise LotNotFoundError(f"Lot {lot_id} not found")
    return LotRead.model_validate(lot)


@lots_router.patch(
    "/{lot_id}",
    response_model=LotRead,
    dependencies=[Depends(require_admin)],
)
def update_lot(
    lot_id: int,
    payload: LotUpdate,
    db: Annotated[Session, Depends(get_db)],
) -> LotRead:
    fields = payload.model_dump(exclude_unset=True)
    lot = lot_repository.update(db, lot_id, **fields)
    db.commit()
    db.refresh(lot)
    return LotRead.model_validate(lot)


@lots_router.delete(
    "/{lot_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_admin)],
)
def delete_lot(
    lot_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> None:
    lot_repository.delete(db, lot_id)
    db.commit()


@lots_router.post(
    "/{lot_id}/status",
    response_model=LotRead,
)
def transition_status(
    lot_id: int,
    payload: LotStatusTransition,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[
        Profile, Depends(require_roles(UserRoleType.ADMIN, UserRoleType.PRICING))
    ],
) -> LotRead:
    lot = lot_service.transition_lot_status(
        db,
        lot_id=lot_id,
        new_status=payload.new_status,
        reason=payload.reason,
        triggering_user_email=current_user.email,
    )
    db.commit()
    db.refresh(lot)
    return LotRead.model_validate(lot)


@lots_router.get(
    "/{lot_id}/status-history",
    response_model=list[StatusHistoryRead],
    dependencies=[Depends(get_current_user)],
)
def get_status_history(
    lot_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> list[StatusHistoryRead]:
    if lot_repository.get(db, lot_id) is None:
        raise LotNotFoundError(f"Lot {lot_id} not found")
    rows = status_history_repository.list_by_lot(db, lot_id)
    return [StatusHistoryRead.model_validate(r) for r in rows]

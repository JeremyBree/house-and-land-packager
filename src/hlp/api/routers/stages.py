"""Estate stage router."""

from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from hlp.api.deps import get_current_user, get_db, require_admin
from hlp.api.schemas.stage import (
    StageCreate,
    StageDetailRead,
    StageRead,
    StageUpdate,
)
from hlp.repositories import estate_repository, stage_repository
from hlp.shared.exceptions import NotFoundError, StageNotFoundError

estates_scoped_router = APIRouter(prefix="/api/estates", tags=["stages"])
stages_router = APIRouter(prefix="/api/stages", tags=["stages"])


@estates_scoped_router.get(
    "/{estate_id}/stages",
    response_model=list[StageRead],
    dependencies=[Depends(get_current_user)],
)
def list_stages_for_estate(
    estate_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> list[StageRead]:
    if estate_repository.get(db, estate_id) is None:
        raise NotFoundError(f"Estate {estate_id} not found")
    stages = stage_repository.list_by_estate(db, estate_id)
    return [StageRead.model_validate(s) for s in stages]


@estates_scoped_router.post(
    "/{estate_id}/stages",
    response_model=StageRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)],
)
def create_stage(
    estate_id: int,
    payload: StageCreate,
    db: Annotated[Session, Depends(get_db)],
) -> StageRead:
    if estate_repository.get(db, estate_id) is None:
        raise NotFoundError(f"Estate {estate_id} not found")
    stage = stage_repository.create(db, estate_id=estate_id, **payload.model_dump())
    db.commit()
    db.refresh(stage)
    return StageRead.model_validate(stage)


@stages_router.get(
    "/{stage_id}",
    response_model=StageDetailRead,
    dependencies=[Depends(get_current_user)],
)
def get_stage(
    stage_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> StageDetailRead:
    result = stage_repository.get_with_stats(db, stage_id)
    if result is None:
        raise StageNotFoundError(f"Stage {stage_id} not found")
    stage, lot_count_actual, breakdown = result
    return StageDetailRead(
        stage_id=stage.stage_id,
        estate_id=stage.estate_id,
        name=stage.name,
        lot_count=stage.lot_count,
        status=stage.status,
        release_date=stage.release_date,
        created_at=stage.created_at,
        updated_at=stage.updated_at,
        lot_count_actual=lot_count_actual,
        status_breakdown=breakdown,
    )


@stages_router.patch(
    "/{stage_id}",
    response_model=StageRead,
    dependencies=[Depends(require_admin)],
)
def update_stage(
    stage_id: int,
    payload: StageUpdate,
    db: Annotated[Session, Depends(get_db)],
) -> StageRead:
    fields = payload.model_dump(exclude_unset=True)
    stage = stage_repository.update(db, stage_id, **fields)
    db.commit()
    db.refresh(stage)
    return StageRead.model_validate(stage)


@stages_router.delete(
    "/{stage_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_admin)],
)
def delete_stage(
    stage_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> None:
    stage_repository.delete(db, stage_id)
    db.commit()

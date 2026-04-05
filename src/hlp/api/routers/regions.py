"""Region router."""

from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from hlp.api.deps import get_current_user, get_db, require_admin
from hlp.api.schemas.region import RegionCreate, RegionRead, RegionUpdate
from hlp.repositories import region_repository
from hlp.shared.exceptions import NotFoundError

router = APIRouter(prefix="/api/regions", tags=["regions"])


@router.get("", response_model=list[RegionRead], dependencies=[Depends(get_current_user)])
def list_regions(db: Annotated[Session, Depends(get_db)]) -> list[RegionRead]:
    return [RegionRead.model_validate(r) for r in region_repository.list_all(db)]


@router.post(
    "",
    response_model=RegionRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)],
)
def create_region(
    payload: RegionCreate,
    db: Annotated[Session, Depends(get_db)],
) -> RegionRead:
    region = region_repository.create(db, name=payload.name)
    db.commit()
    db.refresh(region)
    return RegionRead.model_validate(region)


@router.patch(
    "/{region_id}",
    response_model=RegionRead,
    dependencies=[Depends(require_admin)],
)
def update_region(
    region_id: int,
    payload: RegionUpdate,
    db: Annotated[Session, Depends(get_db)],
) -> RegionRead:
    region = region_repository.update(db, region_id, name=payload.name)
    db.commit()
    db.refresh(region)
    return RegionRead.model_validate(region)


@router.delete(
    "/{region_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_admin)],
)
def delete_region(
    region_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> None:
    existing = region_repository.get(db, region_id)
    if existing is None:
        raise NotFoundError(f"Region {region_id} not found")
    region_repository.delete(db, region_id)
    db.commit()

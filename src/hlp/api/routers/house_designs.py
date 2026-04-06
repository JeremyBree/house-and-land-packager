"""House design catalog router."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from hlp.api.deps import get_current_user, get_db
from hlp.api.schemas.house_design_schema import (
    HouseDesignDetailRead,
    HouseDesignRead,
    HouseFacadeRead,
)
from hlp.repositories import house_design_repository
from hlp.shared.exceptions import NotFoundError

router = APIRouter(prefix="/api/house-designs", tags=["house-designs"])


@router.get("", response_model=list[HouseDesignRead], dependencies=[Depends(get_current_user)])
def list_house_designs(
    db: Annotated[Session, Depends(get_db)],
    brand: str = Query(default="Hermitage Homes"),
) -> list[HouseDesignRead]:
    designs = house_design_repository.list_by_brand(db, brand)
    return [HouseDesignRead.model_validate(d) for d in designs]


@router.get("/{design_id}", response_model=HouseDesignDetailRead, dependencies=[Depends(get_current_user)])
def get_house_design(
    design_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> HouseDesignDetailRead:
    design = house_design_repository.get(db, design_id)
    if design is None:
        raise NotFoundError(f"House design {design_id} not found")
    return HouseDesignDetailRead.model_validate(design)


@router.get("/{design_id}/facades", response_model=list[HouseFacadeRead], dependencies=[Depends(get_current_user)])
def list_facades(
    design_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> list[HouseFacadeRead]:
    design = house_design_repository.get(db, design_id)
    if design is None:
        raise NotFoundError(f"House design {design_id} not found")
    facades = house_design_repository.list_facades(db, design_id)
    return [HouseFacadeRead.model_validate(f) for f in facades]

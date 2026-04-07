"""House design catalog router — full CRUD for designs and facades."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from hlp.api.deps import get_current_user, get_db, require_admin
from hlp.api.schemas.house_design_schema import (
    EnergyRatingCreate,
    EnergyRatingRead,
    EnergyRatingUpdate,
    HouseDesignCreate,
    HouseDesignDetailRead,
    HouseDesignRead,
    HouseDesignUpdate,
    HouseFacadeCreate,
    HouseFacadeRead,
    HouseFacadeUpdate,
)
from hlp.repositories import house_design_repository
from hlp.shared.exceptions import NotFoundError

router = APIRouter(prefix="/api/house-designs", tags=["house-designs"])


@router.get("", response_model=list[HouseDesignRead], dependencies=[Depends(get_current_user)])
def list_house_designs(
    db: Annotated[Session, Depends(get_db)],
    brand: str = Query(default="Hermitage Homes"),
    include_inactive: bool = Query(default=False),
) -> list[HouseDesignRead]:
    if include_inactive:
        designs = house_design_repository.list_all_by_brand(db, brand)
    else:
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


@router.post(
    "",
    response_model=HouseDesignRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)],
)
def create_house_design(
    payload: HouseDesignCreate,
    db: Annotated[Session, Depends(get_db)],
) -> HouseDesignRead:
    design = house_design_repository.create_design(db, **payload.model_dump())
    db.commit()
    db.refresh(design)
    return HouseDesignRead.model_validate(design)


@router.patch(
    "/{design_id}",
    response_model=HouseDesignRead,
    dependencies=[Depends(require_admin)],
)
def update_house_design(
    design_id: int,
    payload: HouseDesignUpdate,
    db: Annotated[Session, Depends(get_db)],
) -> HouseDesignRead:
    design = house_design_repository.update_design(
        db, design_id, **payload.model_dump(exclude_unset=True)
    )
    db.commit()
    db.refresh(design)
    return HouseDesignRead.model_validate(design)


@router.delete(
    "/{design_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_admin)],
)
def delete_house_design(
    design_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> None:
    house_design_repository.delete_design(db, design_id)
    db.commit()


# ---- Facades ----

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


@router.post(
    "/{design_id}/facades",
    response_model=HouseFacadeRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)],
)
def create_facade(
    design_id: int,
    payload: HouseFacadeCreate,
    db: Annotated[Session, Depends(get_db)],
) -> HouseFacadeRead:
    design = house_design_repository.get(db, design_id)
    if design is None:
        raise NotFoundError(f"House design {design_id} not found")
    facade = house_design_repository.create_facade(db, design_id=design_id, **payload.model_dump())
    db.commit()
    db.refresh(facade)
    return HouseFacadeRead.model_validate(facade)


@router.patch(
    "/{design_id}/facades/{facade_id}",
    response_model=HouseFacadeRead,
    dependencies=[Depends(require_admin)],
)
def update_facade(
    design_id: int,
    facade_id: int,
    payload: HouseFacadeUpdate,
    db: Annotated[Session, Depends(get_db)],
) -> HouseFacadeRead:
    facade = house_design_repository.update_facade(
        db, facade_id, **payload.model_dump(exclude_unset=True)
    )
    db.commit()
    db.refresh(facade)
    return HouseFacadeRead.model_validate(facade)


@router.delete(
    "/{design_id}/facades/{facade_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_admin)],
)
def delete_facade(
    design_id: int,
    facade_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> None:
    house_design_repository.delete_facade(db, facade_id)
    db.commit()


# ---- Energy Ratings ----

@router.get(
    "/{design_id}/energy-ratings",
    response_model=list[EnergyRatingRead],
    dependencies=[Depends(get_current_user)],
)
def list_energy_ratings(
    design_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> list[EnergyRatingRead]:
    design = house_design_repository.get(db, design_id)
    if design is None:
        raise NotFoundError(f"House design {design_id} not found")
    ratings = house_design_repository.list_energy_ratings(db, design_id)
    return [EnergyRatingRead.model_validate(r) for r in ratings]


@router.post(
    "/{design_id}/energy-ratings",
    response_model=EnergyRatingRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)],
)
def create_energy_rating(
    design_id: int,
    payload: EnergyRatingCreate,
    db: Annotated[Session, Depends(get_db)],
) -> EnergyRatingRead:
    design = house_design_repository.get(db, design_id)
    if design is None:
        raise NotFoundError(f"House design {design_id} not found")
    rating = house_design_repository.create_energy_rating(db, design_id=design_id, **payload.model_dump())
    db.commit()
    db.refresh(rating)
    return EnergyRatingRead.model_validate(rating)


@router.patch(
    "/{design_id}/energy-ratings/{rating_id}",
    response_model=EnergyRatingRead,
    dependencies=[Depends(require_admin)],
)
def update_energy_rating(
    design_id: int,
    rating_id: int,
    payload: EnergyRatingUpdate,
    db: Annotated[Session, Depends(get_db)],
) -> EnergyRatingRead:
    rating = house_design_repository.update_energy_rating(
        db, rating_id, **payload.model_dump(exclude_unset=True)
    )
    db.commit()
    db.refresh(rating)
    return EnergyRatingRead.model_validate(rating)


@router.delete(
    "/{design_id}/energy-ratings/{rating_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_admin)],
)
def delete_energy_rating(
    design_id: int,
    rating_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> None:
    house_design_repository.delete_energy_rating(db, rating_id)
    db.commit()

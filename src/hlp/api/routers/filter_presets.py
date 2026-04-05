"""Filter preset router — user-scoped CRUD for saved LSI filters."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from hlp.api.deps import get_current_user, get_db
from hlp.api.schemas.filter_preset import (
    FilterPresetCreate,
    FilterPresetRead,
    FilterPresetUpdate,
)
from hlp.models.profile import Profile
from hlp.repositories import filter_preset_repository
from hlp.shared.exceptions import (
    DuplicatePresetNameError,
    FilterPresetNotFoundError,
)

router = APIRouter(prefix="/api/filter-presets", tags=["filter-presets"])


@router.get("", response_model=list[FilterPresetRead])
def list_presets(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Profile, Depends(get_current_user)],
) -> list[FilterPresetRead]:
    presets = filter_preset_repository.list_by_profile(db, current_user.profile_id)
    return [FilterPresetRead.model_validate(p) for p in presets]


@router.post(
    "",
    response_model=FilterPresetRead,
    status_code=status.HTTP_201_CREATED,
)
def create_preset(
    payload: FilterPresetCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Profile, Depends(get_current_user)],
) -> FilterPresetRead:
    existing = filter_preset_repository.get_by_name(
        db, current_user.profile_id, payload.name
    )
    if existing is not None:
        raise DuplicatePresetNameError(
            f"You already have a filter preset named '{payload.name}'"
        )
    preset = filter_preset_repository.create(
        db,
        profile_id=current_user.profile_id,
        name=payload.name,
        filters=payload.filters.model_dump(mode="json"),
    )
    db.commit()
    db.refresh(preset)
    return FilterPresetRead.model_validate(preset)


@router.get("/{preset_id}", response_model=FilterPresetRead)
def get_preset(
    preset_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Profile, Depends(get_current_user)],
) -> FilterPresetRead:
    preset = filter_preset_repository.get(db, preset_id, current_user.profile_id)
    if preset is None:
        raise FilterPresetNotFoundError(f"Filter preset {preset_id} not found")
    return FilterPresetRead.model_validate(preset)


@router.patch("/{preset_id}", response_model=FilterPresetRead)
def update_preset(
    preset_id: int,
    payload: FilterPresetUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Profile, Depends(get_current_user)],
) -> FilterPresetRead:
    # Ownership check + 404 if not found for this user.
    existing = filter_preset_repository.get(db, preset_id, current_user.profile_id)
    if existing is None:
        raise FilterPresetNotFoundError(f"Filter preset {preset_id} not found")

    # Name uniqueness check if renaming.
    if payload.name is not None and payload.name != existing.name:
        name_clash = filter_preset_repository.get_by_name(
            db, current_user.profile_id, payload.name
        )
        if name_clash is not None:
            raise DuplicatePresetNameError(
                f"You already have a filter preset named '{payload.name}'"
            )

    update_fields: dict = {}
    if payload.name is not None:
        update_fields["name"] = payload.name
    if payload.filters is not None:
        update_fields["filters"] = payload.filters.model_dump(mode="json")

    preset = filter_preset_repository.update(
        db, preset_id, current_user.profile_id, **update_fields
    )
    db.commit()
    db.refresh(preset)
    return FilterPresetRead.model_validate(preset)


@router.delete("/{preset_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_preset(
    preset_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Profile, Depends(get_current_user)],
) -> None:
    existing = filter_preset_repository.get(db, preset_id, current_user.profile_id)
    if existing is None:
        raise FilterPresetNotFoundError(f"Filter preset {preset_id} not found")
    filter_preset_repository.delete(db, preset_id, current_user.profile_id)
    db.commit()

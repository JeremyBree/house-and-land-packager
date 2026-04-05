"""FilterPreset data access — user-scoped saved LSI filters."""

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from hlp.models.filter_preset import FilterPreset
from hlp.shared.exceptions import FilterPresetNotFoundError


def list_by_profile(db: Session, profile_id: int) -> list[FilterPreset]:
    stmt = (
        select(FilterPreset)
        .where(FilterPreset.profile_id == profile_id)
        .order_by(FilterPreset.name)
    )
    return list(db.execute(stmt).scalars().all())


def get(db: Session, preset_id: int, profile_id: int) -> FilterPreset | None:
    stmt = select(FilterPreset).where(
        FilterPreset.preset_id == preset_id,
        FilterPreset.profile_id == profile_id,
    )
    return db.execute(stmt).scalar_one_or_none()


def get_by_name(db: Session, profile_id: int, name: str) -> FilterPreset | None:
    stmt = select(FilterPreset).where(
        FilterPreset.profile_id == profile_id,
        FilterPreset.name == name,
    )
    return db.execute(stmt).scalar_one_or_none()


def create(
    db: Session, profile_id: int, name: str, filters: dict[str, Any]
) -> FilterPreset:
    preset = FilterPreset(profile_id=profile_id, name=name, filters=filters)
    db.add(preset)
    db.flush()
    return preset


def update(db: Session, preset_id: int, profile_id: int, **fields: Any) -> FilterPreset:
    preset = get(db, preset_id, profile_id)
    if preset is None:
        raise FilterPresetNotFoundError(f"Filter preset {preset_id} not found")
    for k, v in fields.items():
        if v is not None:
            setattr(preset, k, v)
    db.flush()
    return preset


def delete(db: Session, preset_id: int, profile_id: int) -> None:
    preset = get(db, preset_id, profile_id)
    if preset is None:
        raise FilterPresetNotFoundError(f"Filter preset {preset_id} not found")
    db.delete(preset)
    db.flush()

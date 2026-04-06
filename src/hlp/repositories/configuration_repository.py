"""Configuration data access."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from hlp.models.configuration import Configuration
from hlp.shared.exceptions import NotFoundError


def list_filtered(
    db: Session,
    config_type: str | None = None,
    enabled: bool | None = None,
) -> list[Configuration]:
    stmt = select(Configuration).order_by(Configuration.priority_rank, Configuration.config_id)
    if config_type is not None:
        stmt = stmt.where(Configuration.config_type == config_type)
    if enabled is not None:
        stmt = stmt.where(Configuration.enabled == enabled)
    return list(db.execute(stmt).scalars().all())


def get(db: Session, config_id: int) -> Configuration | None:
    return db.get(Configuration, config_id)


def get_or_raise(db: Session, config_id: int) -> Configuration:
    obj = get(db, config_id)
    if obj is None:
        raise NotFoundError(f"Configuration {config_id} not found")
    return obj


def create(db: Session, **fields) -> Configuration:
    obj = Configuration(**fields)
    db.add(obj)
    db.flush()
    return obj


def update(db: Session, config_id: int, **fields) -> Configuration:
    obj = get_or_raise(db, config_id)
    for key, value in fields.items():
        if value is not None:
            setattr(obj, key, value)
    db.flush()
    return obj


def delete(db: Session, config_id: int) -> None:
    obj = get_or_raise(db, config_id)
    db.delete(obj)
    db.flush()


def toggle_enabled(db: Session, config_id: int) -> Configuration:
    obj = get_or_raise(db, config_id)
    obj.enabled = not obj.enabled
    db.flush()
    return obj

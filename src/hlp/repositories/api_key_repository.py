"""API key data access."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from hlp.models.api_key import ApiKey
from hlp.shared.exceptions import NotFoundError


def list_all(db: Session) -> list[ApiKey]:
    stmt = select(ApiKey).order_by(ApiKey.created_at.desc())
    return list(db.execute(stmt).scalars().all())


def get(db: Session, key_id: int) -> ApiKey | None:
    return db.get(ApiKey, key_id)


def create(db: Session, **fields) -> ApiKey:
    api_key = ApiKey(**fields)
    db.add(api_key)
    db.flush()
    return api_key


def update(db: Session, key_id: int, **fields) -> ApiKey:
    api_key = get(db, key_id)
    if api_key is None:
        raise NotFoundError(f"API key {key_id} not found")
    for k, v in fields.items():
        if v is not None:
            setattr(api_key, k, v)
    db.flush()
    return api_key


def delete(db: Session, key_id: int) -> None:
    api_key = get(db, key_id)
    if api_key is None:
        raise NotFoundError(f"API key {key_id} not found")
    db.delete(api_key)
    db.flush()

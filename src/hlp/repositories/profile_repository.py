"""Profile (user) data access."""

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from hlp.models.profile import Profile


def get_by_email(db: Session, email: str) -> Profile | None:
    stmt = (
        select(Profile)
        .where(func.lower(Profile.email) == email.lower())
        .options(selectinload(Profile.user_roles))
    )
    return db.execute(stmt).scalar_one_or_none()


def get_by_id(db: Session, profile_id: int) -> Profile | None:
    stmt = (
        select(Profile)
        .where(Profile.profile_id == profile_id)
        .options(selectinload(Profile.user_roles))
    )
    return db.execute(stmt).scalar_one_or_none()


def list_paginated(
    db: Session,
    page: int,
    size: int,
    search: str | None = None,
) -> tuple[list[Profile], int]:
    base = select(Profile)
    if search:
        pattern = f"%{search.lower()}%"
        base = base.where(
            or_(
                func.lower(Profile.email).like(pattern),
                func.lower(Profile.first_name).like(pattern),
                func.lower(Profile.last_name).like(pattern),
            )
        )

    total = db.execute(select(func.count()).select_from(base.subquery())).scalar_one()

    stmt = (
        base.options(selectinload(Profile.user_roles))
        .order_by(Profile.profile_id)
        .offset((page - 1) * size)
        .limit(size)
    )
    items = list(db.execute(stmt).scalars().all())
    return items, int(total)


def create(db: Session, **fields) -> Profile:
    profile = Profile(**fields)
    db.add(profile)
    db.flush()
    return profile


def update(db: Session, profile_id: int, **fields) -> Profile:
    profile = get_by_id(db, profile_id)
    if profile is None:
        from hlp.shared.exceptions import UserNotFoundError

        raise UserNotFoundError(f"Profile {profile_id} not found")
    for k, v in fields.items():
        if v is not None:
            setattr(profile, k, v)
    db.flush()
    return profile


def delete(db: Session, profile_id: int) -> None:
    profile = get_by_id(db, profile_id)
    if profile is None:
        from hlp.shared.exceptions import UserNotFoundError

        raise UserNotFoundError(f"Profile {profile_id} not found")
    db.delete(profile)
    db.flush()

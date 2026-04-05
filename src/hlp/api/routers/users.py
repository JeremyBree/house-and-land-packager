"""User management router (admin only)."""

import math
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from hlp.api.deps import get_db, require_admin
from hlp.api.schemas.common import PaginatedResponse
from hlp.api.schemas.user import (
    UserCreate,
    UserRead,
    UserRolesUpdate,
    UserUpdate,
)
from hlp.models.profile import Profile
from hlp.repositories import profile_repository
from hlp.shared import user_service

router = APIRouter(
    prefix="/api/users",
    tags=["users"],
    dependencies=[Depends(require_admin)],
)


def _to_read(p: Profile) -> UserRead:
    return UserRead(
        profile_id=p.profile_id,
        email=p.email,
        first_name=p.first_name,
        last_name=p.last_name,
        job_title=p.job_title,
        email_verified=p.email_verified,
        roles=[ur.role for ur in p.user_roles],
        created_at=p.created_at,
    )


@router.get("", response_model=PaginatedResponse[UserRead])
def list_users(
    db: Annotated[Session, Depends(get_db)],
    page: int = Query(1, ge=1),
    size: int = Query(25, ge=1, le=200),
    search: str | None = None,
) -> PaginatedResponse[UserRead]:
    items, total = profile_repository.list_paginated(db, page, size, search)
    pages = math.ceil(total / size) if size else 0
    return PaginatedResponse[UserRead](
        items=[_to_read(p) for p in items],
        total=total,
        page=page,
        size=size,
        pages=pages,
    )


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: UserCreate,
    db: Annotated[Session, Depends(get_db)],
) -> UserRead:
    profile = user_service.create_user_with_roles(
        db,
        email=payload.email,
        password=payload.password,
        first_name=payload.first_name,
        last_name=payload.last_name,
        job_title=payload.job_title,
        roles=payload.roles,
    )
    db.commit()
    db.refresh(profile)
    return _to_read(profile)


@router.get("/{profile_id}", response_model=UserRead)
def get_user(
    profile_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> UserRead:
    from hlp.shared.exceptions import UserNotFoundError

    profile = profile_repository.get_by_id(db, profile_id)
    if profile is None:
        raise UserNotFoundError(f"Profile {profile_id} not found")
    return _to_read(profile)


@router.patch("/{profile_id}", response_model=UserRead)
def update_user(
    profile_id: int,
    payload: UserUpdate,
    db: Annotated[Session, Depends(get_db)],
) -> UserRead:
    profile = user_service.update_user(
        db,
        profile_id,
        first_name=payload.first_name,
        last_name=payload.last_name,
        job_title=payload.job_title,
    )
    db.commit()
    db.refresh(profile)
    return _to_read(profile)


@router.put("/{profile_id}/roles", response_model=UserRead)
def set_roles(
    profile_id: int,
    payload: UserRolesUpdate,
    db: Annotated[Session, Depends(get_db)],
) -> UserRead:
    profile = user_service.set_user_roles(db, profile_id, payload.roles)
    db.commit()
    db.refresh(profile)
    return _to_read(profile)


@router.delete("/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    profile_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> None:
    user_service.delete_user(db, profile_id)
    db.commit()

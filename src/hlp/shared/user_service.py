"""User management service — create/update/delete users and roles."""

from sqlalchemy.orm import Session

from hlp.models.enums import UserRoleType
from hlp.models.profile import Profile
from hlp.models.user_role import UserRole
from hlp.repositories import profile_repository
from hlp.shared.exceptions import (
    DuplicateEmailError,
    MinRolesRequiredError,
    UserNotFoundError,
)
from hlp.shared.security import hash_password


def create_user_with_roles(
    db: Session,
    email: str,
    password: str,
    first_name: str,
    last_name: str,
    job_title: str | None,
    roles: list[UserRoleType],
) -> Profile:
    if not roles:
        raise MinRolesRequiredError("At least one role is required")

    existing = profile_repository.get_by_email(db, email)
    if existing is not None:
        raise DuplicateEmailError(f"Email already registered: {email}")

    profile = profile_repository.create(
        db,
        email=email,
        password_hash=hash_password(password),
        first_name=first_name,
        last_name=last_name,
        job_title=job_title,
        email_verified=False,
    )
    for role in _dedupe_roles(roles):
        db.add(UserRole(profile_id=profile.profile_id, role=role))
    db.flush()
    db.refresh(profile)
    return profile


def update_user(db: Session, profile_id: int, **fields) -> Profile:
    profile = profile_repository.get_by_id(db, profile_id)
    if profile is None:
        raise UserNotFoundError(f"Profile {profile_id} not found")
    allowed = {"first_name", "last_name", "job_title"}
    updates = {k: v for k, v in fields.items() if k in allowed and v is not None}
    for k, v in updates.items():
        setattr(profile, k, v)
    db.flush()
    db.refresh(profile)
    return profile


def set_user_roles(
    db: Session, profile_id: int, roles: list[UserRoleType]
) -> Profile:
    if not roles:
        raise MinRolesRequiredError("At least one role is required")

    profile = profile_repository.get_by_id(db, profile_id)
    if profile is None:
        raise UserNotFoundError(f"Profile {profile_id} not found")

    for ur in list(profile.user_roles):
        db.delete(ur)
    db.flush()

    for role in _dedupe_roles(roles):
        db.add(UserRole(profile_id=profile.profile_id, role=role))
    db.flush()
    db.refresh(profile)
    return profile


def delete_user(db: Session, profile_id: int) -> None:
    profile = profile_repository.get_by_id(db, profile_id)
    if profile is None:
        raise UserNotFoundError(f"Profile {profile_id} not found")
    db.delete(profile)
    db.flush()


def _dedupe_roles(roles: list[UserRoleType]) -> list[UserRoleType]:
    return list(dict.fromkeys(roles))

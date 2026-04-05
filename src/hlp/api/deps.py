"""FastAPI dependencies: DB session, auth, role enforcement."""

from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from hlp.database import get_db
from hlp.models.enums import UserRoleType
from hlp.models.profile import Profile
from hlp.repositories import profile_repository
from hlp.shared.exceptions import AuthenticationError, NotAuthorizedError
from hlp.shared.security import decode_token

__all__ = [
    "get_db",
    "oauth2_scheme",
    "get_current_user",
    "require_roles",
    "require_admin",
]

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> Profile:
    """Resolve the current user from the bearer token."""
    payload = decode_token(token)
    profile = profile_repository.get_by_id(db, payload.sub)
    if profile is None:
        raise AuthenticationError("User no longer exists")
    return profile


def require_roles(*roles: UserRoleType):
    """Dependency factory — requires the user to have at least one of the listed roles."""
    required = set(roles)

    def _checker(
        current_user: Annotated[Profile, Depends(get_current_user)],
    ) -> Profile:
        user_roles = {ur.role for ur in current_user.user_roles}
        if not (required & user_roles):
            raise NotAuthorizedError(
                f"Requires one of roles: {', '.join(r.value for r in roles)}"
            )
        return current_user

    return _checker


require_admin = require_roles(UserRoleType.ADMIN)

"""Authentication service — verify credentials and mint tokens."""

from sqlalchemy.orm import Session

from hlp.api.schemas.auth import TokenResponse
from hlp.config import get_settings
from hlp.models.profile import Profile
from hlp.repositories import profile_repository
from hlp.shared.exceptions import AuthenticationError
from hlp.shared.security import create_access_token, verify_password


def authenticate(db: Session, email: str, password: str) -> Profile:
    """Verify credentials and return the Profile. Raises AuthenticationError."""
    profile = profile_repository.get_by_email(db, email)
    if profile is None:
        raise AuthenticationError("Invalid email or password")
    if not verify_password(password, profile.password_hash):
        raise AuthenticationError("Invalid email or password")
    return profile


def build_token_for(profile: Profile) -> TokenResponse:
    """Produce a signed access token for a Profile."""
    settings = get_settings()
    roles = [ur.role.value for ur in profile.user_roles]
    token = create_access_token(subject=profile.profile_id, roles=roles, email=profile.email)
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=settings.jwt_expire_minutes * 60,
    )

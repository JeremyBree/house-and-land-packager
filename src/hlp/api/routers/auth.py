"""Auth router: login + current-user."""

from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from hlp.api.deps import get_current_user, get_db
from hlp.api.schemas.auth import TokenResponse
from hlp.api.schemas.user import UserRead
from hlp.models.profile import Profile
from hlp.shared import auth_service

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(get_db)],
) -> TokenResponse:
    profile = auth_service.authenticate(db, form_data.username, form_data.password)
    return auth_service.build_token_for(profile)


@router.get("/me", response_model=UserRead)
def me(current_user: Annotated[Profile, Depends(get_current_user)]) -> UserRead:
    return UserRead(
        profile_id=current_user.profile_id,
        email=current_user.email,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        job_title=current_user.job_title,
        email_verified=current_user.email_verified,
        roles=[ur.role for ur in current_user.user_roles],
        created_at=current_user.created_at,
    )

"""API key admin management router."""

from typing import Annotated

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from hlp.api.deps import get_db, require_admin
from hlp.api.schemas.api_key_schema import (
    ApiKeyCreateInput,
    ApiKeyCreateResponse,
    ApiKeyRead,
    ApiKeyUpdate,
)
from hlp.models.profile import Profile
from hlp.repositories import api_key_repository
from hlp.shared.api_key_service import create_api_key, revoke_api_key
from hlp.shared.exceptions import NotFoundError

router = APIRouter(prefix="/api/api-keys", tags=["api-keys"])


@router.get("", response_model=list[ApiKeyRead])
def list_keys(
    _admin: Annotated[Profile, Depends(require_admin)],
    db: Annotated[Session, Depends(get_db)],
):
    """List all API keys (key_hash is never returned)."""
    return api_key_repository.list_all(db)


@router.post("", response_model=ApiKeyCreateResponse, status_code=201)
def create_key(
    body: ApiKeyCreateInput,
    admin: Annotated[Profile, Depends(require_admin)],
    db: Annotated[Session, Depends(get_db)],
):
    """Create a new API key. The raw_key is only returned once."""
    api_key, raw_key = create_api_key(
        db,
        agent_name=body.agent_name,
        agent_type=body.agent_type,
        scopes=body.scopes,
        created_by=admin.profile_id,
        expires_at=body.expires_at,
        notes=body.notes,
    )
    db.commit()
    db.refresh(api_key)
    resp = ApiKeyCreateResponse.model_validate(api_key)
    resp.raw_key = raw_key
    return resp


@router.patch("/{key_id}", response_model=ApiKeyRead)
def update_key(
    key_id: int,
    body: ApiKeyUpdate,
    _admin: Annotated[Profile, Depends(require_admin)],
    db: Annotated[Session, Depends(get_db)],
):
    """Update an API key's metadata."""
    updates = body.model_dump(exclude_unset=True)
    if not updates:
        existing = api_key_repository.get(db, key_id)
        if existing is None:
            raise NotFoundError(f"API key {key_id} not found")
        return existing
    api_key = api_key_repository.update(db, key_id, **updates)
    db.commit()
    db.refresh(api_key)
    return api_key


@router.delete("/{key_id}", status_code=204)
def delete_key(
    key_id: int,
    _admin: Annotated[Profile, Depends(require_admin)],
    db: Annotated[Session, Depends(get_db)],
):
    """Delete an API key permanently."""
    api_key_repository.delete(db, key_id)
    db.commit()
    return Response(status_code=204)


@router.post("/{key_id}/revoke", response_model=ApiKeyRead)
def revoke_key(
    key_id: int,
    _admin: Annotated[Profile, Depends(require_admin)],
    db: Annotated[Session, Depends(get_db)],
):
    """Revoke an API key (set is_active=false)."""
    api_key = revoke_api_key(db, key_id)
    if api_key is None:
        raise NotFoundError(f"API key {key_id} not found")
    db.commit()
    db.refresh(api_key)
    return api_key

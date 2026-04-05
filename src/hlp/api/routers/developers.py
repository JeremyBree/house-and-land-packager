"""Developer router."""

from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from hlp.api.deps import get_current_user, get_db, require_admin
from hlp.api.schemas.developer import (
    DeveloperCreate,
    DeveloperRead,
    DeveloperUpdate,
)
from hlp.repositories import developer_repository
from hlp.shared.exceptions import NotFoundError

router = APIRouter(prefix="/api/developers", tags=["developers"])


@router.get(
    "",
    response_model=list[DeveloperRead],
    dependencies=[Depends(get_current_user)],
)
def list_developers(db: Annotated[Session, Depends(get_db)]) -> list[DeveloperRead]:
    return [DeveloperRead.model_validate(d) for d in developer_repository.list_all(db)]


@router.post(
    "",
    response_model=DeveloperRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)],
)
def create_developer(
    payload: DeveloperCreate,
    db: Annotated[Session, Depends(get_db)],
) -> DeveloperRead:
    fields = payload.model_dump()
    if fields.get("contact_email") is not None:
        fields["contact_email"] = str(fields["contact_email"])
    dev = developer_repository.create(db, **fields)
    db.commit()
    db.refresh(dev)
    return DeveloperRead.model_validate(dev)


@router.patch(
    "/{developer_id}",
    response_model=DeveloperRead,
    dependencies=[Depends(require_admin)],
)
def update_developer(
    developer_id: int,
    payload: DeveloperUpdate,
    db: Annotated[Session, Depends(get_db)],
) -> DeveloperRead:
    fields = payload.model_dump(exclude_unset=True)
    if fields.get("contact_email") is not None:
        fields["contact_email"] = str(fields["contact_email"])
    dev = developer_repository.update(db, developer_id, **fields)
    db.commit()
    db.refresh(dev)
    return DeveloperRead.model_validate(dev)


@router.delete(
    "/{developer_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_admin)],
)
def delete_developer(
    developer_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> None:
    existing = developer_repository.get(db, developer_id)
    if existing is None:
        raise NotFoundError(f"Developer {developer_id} not found")
    developer_repository.delete(db, developer_id)
    db.commit()

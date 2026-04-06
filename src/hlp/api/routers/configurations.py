"""Configuration management router — admin only."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from hlp.api.deps import get_db, require_admin
from hlp.api.schemas.configuration import (
    ConfigurationCreate,
    ConfigurationRead,
    ConfigurationUpdate,
)
from hlp.repositories import configuration_repository

router = APIRouter(prefix="/api/configurations", tags=["configurations"])


@router.get(
    "",
    response_model=list[ConfigurationRead],
    dependencies=[Depends(require_admin)],
)
def list_configurations(
    db: Annotated[Session, Depends(get_db)],
    type: str | None = Query(None, alias="type"),
    enabled: bool | None = None,
) -> list[ConfigurationRead]:
    items = configuration_repository.list_filtered(db, config_type=type, enabled=enabled)
    return [ConfigurationRead.from_model(c) for c in items]


@router.post(
    "",
    response_model=ConfigurationRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)],
)
def create_configuration(
    db: Annotated[Session, Depends(get_db)],
    payload: ConfigurationCreate,
) -> ConfigurationRead:
    obj = configuration_repository.create(db, **payload.model_dump())
    db.commit()
    db.refresh(obj)
    return ConfigurationRead.from_model(obj)


@router.get(
    "/{config_id}",
    response_model=ConfigurationRead,
    dependencies=[Depends(require_admin)],
)
def get_configuration(
    db: Annotated[Session, Depends(get_db)],
    config_id: int,
) -> ConfigurationRead:
    obj = configuration_repository.get_or_raise(db, config_id)
    return ConfigurationRead.from_model(obj)


@router.patch(
    "/{config_id}",
    response_model=ConfigurationRead,
    dependencies=[Depends(require_admin)],
)
def update_configuration(
    db: Annotated[Session, Depends(get_db)],
    config_id: int,
    payload: ConfigurationUpdate,
) -> ConfigurationRead:
    update_data = payload.model_dump(exclude_unset=True)
    obj = configuration_repository.update(db, config_id, **update_data)
    db.commit()
    db.refresh(obj)
    return ConfigurationRead.from_model(obj)


@router.delete(
    "/{config_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_admin)],
)
def delete_configuration(
    db: Annotated[Session, Depends(get_db)],
    config_id: int,
) -> None:
    configuration_repository.delete(db, config_id)
    db.commit()


@router.post(
    "/{config_id}/toggle",
    response_model=ConfigurationRead,
    dependencies=[Depends(require_admin)],
)
def toggle_configuration(
    db: Annotated[Session, Depends(get_db)],
    config_id: int,
) -> ConfigurationRead:
    obj = configuration_repository.toggle_enabled(db, config_id)
    db.commit()
    db.refresh(obj)
    return ConfigurationRead.from_model(obj)

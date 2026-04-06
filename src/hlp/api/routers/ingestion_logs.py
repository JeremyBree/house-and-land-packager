"""Ingestion logs viewer router — admin only."""

import math
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from hlp.api.deps import get_db, require_admin
from hlp.api.schemas.common import PaginatedResponse
from hlp.api.schemas.ingestion_log import IngestionLogRead
from hlp.repositories import ingestion_log_repository

router = APIRouter(prefix="/api/ingestion-logs", tags=["ingestion-logs"])


@router.get(
    "",
    response_model=PaginatedResponse[IngestionLogRead],
    dependencies=[Depends(require_admin)],
)
def list_ingestion_logs(
    db: Annotated[Session, Depends(get_db)],
    page: int = Query(1, ge=1),
    size: int = Query(25, ge=1, le=200),
    agent_type: str | None = None,
    status: str | None = None,
) -> PaginatedResponse[IngestionLogRead]:
    items, total = ingestion_log_repository.list_paginated(
        db, page=page, size=size, agent_type=agent_type, status=status,
    )
    pages = math.ceil(total / size) if size else 0
    return PaginatedResponse[IngestionLogRead](
        items=[IngestionLogRead.model_validate(i) for i in items],
        total=total,
        page=page,
        size=size,
        pages=pages,
    )


@router.get(
    "/{log_id}",
    response_model=IngestionLogRead,
    dependencies=[Depends(require_admin)],
)
def get_ingestion_log(
    db: Annotated[Session, Depends(get_db)],
    log_id: int,
) -> IngestionLogRead:
    obj = ingestion_log_repository.get_or_raise(db, log_id)
    return IngestionLogRead.model_validate(obj)

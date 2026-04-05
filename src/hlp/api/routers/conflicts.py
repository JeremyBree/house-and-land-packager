"""Conflict detection router."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from hlp.api.deps import get_current_user, get_db
from hlp.api.schemas.conflict import ConflictRead, ConflictSummary
from hlp.shared import conflict_service

router = APIRouter(prefix="/api/conflicts", tags=["conflicts"])


@router.get(
    "",
    response_model=list[ConflictRead],
    dependencies=[Depends(get_current_user)],
)
def list_conflicts(
    db: Annotated[Session, Depends(get_db)],
    estate_id: int | None = None,
) -> list[ConflictRead]:
    conflicts = conflict_service.detect_all_conflicts(db, estate_id=estate_id)
    return [ConflictRead.model_validate(c) for c in conflicts]


@router.get(
    "/summary",
    response_model=ConflictSummary,
    dependencies=[Depends(get_current_user)],
)
def get_conflict_summary(
    db: Annotated[Session, Depends(get_db)],
) -> ConflictSummary:
    summary = conflict_service.get_conflict_summary(db)
    return ConflictSummary.model_validate(summary)

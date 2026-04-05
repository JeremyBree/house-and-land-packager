"""Clash rule router."""

from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from hlp.api.deps import get_current_user, get_db, require_admin
from hlp.api.schemas.clash_rule import (
    ClashRuleCopyRequest,
    ClashRuleCreate,
    ClashRuleRead,
    ClashRuleUpdate,
)
from hlp.repositories import clash_rule_repository, estate_repository, stage_repository
from hlp.shared import clash_service
from hlp.shared.exceptions import (
    ClashRuleNotFoundError,
    NotFoundError,
    StageNotFoundError,
)

estate_scoped_router = APIRouter(prefix="/api/estates", tags=["clash-rules"])
stage_scoped_router = APIRouter(prefix="/api/stages", tags=["clash-rules"])
rules_router = APIRouter(prefix="/api/clash-rules", tags=["clash-rules"])
estate_stage_router = APIRouter(prefix="/api/estates", tags=["clash-rules"])


@estate_scoped_router.get(
    "/{estate_id}/clash-rules",
    response_model=list[ClashRuleRead],
    dependencies=[Depends(get_current_user)],
)
def list_estate_clash_rules(
    estate_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> list[ClashRuleRead]:
    if estate_repository.get(db, estate_id) is None:
        raise NotFoundError(f"Estate {estate_id} not found")
    rules = clash_rule_repository.list_by_estate(db, estate_id)
    return [ClashRuleRead.model_validate(r) for r in rules]


@stage_scoped_router.get(
    "/{stage_id}/clash-rules",
    response_model=list[ClashRuleRead],
    dependencies=[Depends(get_current_user)],
)
def list_stage_clash_rules(
    stage_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> list[ClashRuleRead]:
    stage = stage_repository.get(db, stage_id)
    if stage is None:
        raise StageNotFoundError(f"Stage {stage_id} not found")
    rules = clash_rule_repository.list_by_stage(db, stage.estate_id, stage_id)
    return [ClashRuleRead.model_validate(r) for r in rules]


@estate_stage_router.post(
    "/{estate_id}/stages/{stage_id}/clash-rules",
    response_model=ClashRuleRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)],
)
def create_clash_rule(
    estate_id: int,
    stage_id: int,
    payload: ClashRuleCreate,
    db: Annotated[Session, Depends(get_db)],
) -> ClashRuleRead:
    # Override with URL-scoped values
    if estate_repository.get(db, estate_id) is None:
        raise NotFoundError(f"Estate {estate_id} not found")
    stage = stage_repository.get(db, stage_id)
    if stage is None:
        raise StageNotFoundError(f"Stage {stage_id} not found")
    rule = clash_service.create_clash_rule(
        db,
        estate_id=estate_id,
        stage_id=stage_id,
        lot_number=payload.lot_number,
        cannot_match=payload.cannot_match,
    )
    db.commit()
    db.refresh(rule)
    return ClashRuleRead.model_validate(rule)


@rules_router.get(
    "/{rule_id}",
    response_model=ClashRuleRead,
    dependencies=[Depends(get_current_user)],
)
def get_clash_rule(
    rule_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> ClashRuleRead:
    rule = clash_rule_repository.get(db, rule_id)
    if rule is None:
        raise ClashRuleNotFoundError(f"Clash rule {rule_id} not found")
    return ClashRuleRead.model_validate(rule)


@rules_router.patch(
    "/{rule_id}",
    response_model=ClashRuleRead,
    dependencies=[Depends(require_admin)],
)
def update_clash_rule(
    rule_id: int,
    payload: ClashRuleUpdate,
    db: Annotated[Session, Depends(get_db)],
) -> ClashRuleRead:
    rule = clash_service.update_clash_rule(db, rule_id, payload.cannot_match)
    db.commit()
    db.refresh(rule)
    return ClashRuleRead.model_validate(rule)


@rules_router.delete(
    "/{rule_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_admin)],
)
def delete_clash_rule(
    rule_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> None:
    clash_rule_repository.delete(db, rule_id)
    db.commit()


@stage_scoped_router.post(
    "/{stage_id}/clash-rules/copy",
    dependencies=[Depends(require_admin)],
)
def copy_clash_rules(
    stage_id: int,
    payload: ClashRuleCopyRequest,
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    source_stage = stage_repository.get(db, stage_id)
    if source_stage is None:
        raise StageNotFoundError(f"Stage {stage_id} not found")
    target_stage = stage_repository.get(db, payload.target_stage_id)
    if target_stage is None:
        raise StageNotFoundError(f"Stage {payload.target_stage_id} not found")
    if estate_repository.get(db, payload.target_estate_id) is None:
        raise NotFoundError(f"Estate {payload.target_estate_id} not found")
    count = clash_service.copy_clash_rules(
        db,
        source_estate_id=source_stage.estate_id,
        source_stage_id=stage_id,
        target_estate_id=payload.target_estate_id,
        target_stage_id=payload.target_stage_id,
    )
    db.commit()
    return {"copied": count}

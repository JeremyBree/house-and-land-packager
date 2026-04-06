"""Pricing rules and categories router."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from hlp.api.deps import get_db, require_admin
from hlp.api.schemas.pricing_rule import (
    GlobalRuleCreate,
    GlobalRuleRead,
    GlobalRuleUpdate,
    RuleCategoryCreate,
    RuleCategoryRead,
    RuleCategoryUpdate,
    StageRuleCreate,
    StageRuleRead,
    StageRuleUpdate,
)
from hlp.repositories import (
    estate_repository,
    pricing_rule_repository,
    stage_repository,
)
from hlp.shared import pricing_rule_service
from hlp.shared.exceptions import (
    CategoryNotFoundError,
    NotFoundError,
    PricingRuleNotFoundError,
)

categories_router = APIRouter(
    prefix="/api/pricing-rule-categories", tags=["pricing-rules"]
)
rules_router = APIRouter(prefix="/api/pricing-rules", tags=["pricing-rules"])


# ---- Helpers ----


def _enrich_global_rule(
    db: Session, rule: object
) -> GlobalRuleRead:
    """Build GlobalRuleRead with optional category_name."""
    data = GlobalRuleRead.model_validate(rule)
    if rule.category_id:  # type: ignore[union-attr]
        cat = pricing_rule_repository.get_category(db, rule.category_id)  # type: ignore[union-attr]
        if cat:
            data.category_name = cat.name
    return data


def _enrich_stage_rule(
    db: Session, rule: object
) -> StageRuleRead:
    """Build StageRuleRead with estate_name, stage_name, category_name."""
    data = StageRuleRead.model_validate(rule)
    estate = estate_repository.get(db, rule.estate_id)  # type: ignore[union-attr]
    if estate:
        data.estate_name = estate.estate_name
    stage = stage_repository.get(db, rule.stage_id)  # type: ignore[union-attr]
    if stage:
        data.stage_name = stage.name
    if rule.category_id:  # type: ignore[union-attr]
        cat = pricing_rule_repository.get_category(db, rule.category_id)  # type: ignore[union-attr]
        if cat:
            data.category_name = cat.name
    return data


# ---- Categories ----


@categories_router.get(
    "",
    response_model=list[RuleCategoryRead],
    dependencies=[Depends(require_admin)],
)
def list_categories(
    brand: str = Query(...),
    db: Session = Depends(get_db),
) -> list[RuleCategoryRead]:
    cats = pricing_rule_repository.list_categories(db, brand)
    return [RuleCategoryRead.model_validate(c) for c in cats]


@categories_router.post(
    "",
    response_model=RuleCategoryRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)],
)
def create_category(
    payload: RuleCategoryCreate,
    db: Annotated[Session, Depends(get_db)],
) -> RuleCategoryRead:
    cat = pricing_rule_repository.create_category(
        db,
        name=payload.name,
        brand=payload.brand,
        sort_order=payload.sort_order,
    )
    db.commit()
    db.refresh(cat)
    return RuleCategoryRead.model_validate(cat)


@categories_router.patch(
    "/{category_id}",
    response_model=RuleCategoryRead,
    dependencies=[Depends(require_admin)],
)
def update_category(
    category_id: int,
    payload: RuleCategoryUpdate,
    db: Annotated[Session, Depends(get_db)],
) -> RuleCategoryRead:
    cat = pricing_rule_repository.get_category(db, category_id)
    if cat is None:
        raise CategoryNotFoundError(f"Category {category_id} not found")
    updates = payload.model_dump(exclude_unset=True)
    pricing_rule_repository.update_category(db, cat, **updates)
    db.commit()
    db.refresh(cat)
    return RuleCategoryRead.model_validate(cat)


@categories_router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_admin)],
)
def delete_category(
    category_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> None:
    pricing_rule_repository.delete_category(db, category_id)
    db.commit()


# ---- Global Rules ----


@rules_router.get(
    "/global",
    response_model=list[GlobalRuleRead],
    dependencies=[Depends(require_admin)],
)
def list_global_rules(
    brand: str = Query(...),
    db: Session = Depends(get_db),
) -> list[GlobalRuleRead]:
    rules = pricing_rule_repository.list_global_rules(db, brand)
    return [_enrich_global_rule(db, r) for r in rules]


@rules_router.post(
    "/global",
    response_model=GlobalRuleRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)],
)
def create_global_rule(
    payload: GlobalRuleCreate,
    db: Annotated[Session, Depends(get_db)],
) -> GlobalRuleRead:
    rule = pricing_rule_repository.create_global_rule(
        db, **payload.model_dump()
    )
    db.commit()
    db.refresh(rule)
    return _enrich_global_rule(db, rule)


@rules_router.get(
    "/global/{rule_id}",
    response_model=GlobalRuleRead,
    dependencies=[Depends(require_admin)],
)
def get_global_rule(
    rule_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> GlobalRuleRead:
    rule = pricing_rule_repository.get_global_rule(db, rule_id)
    if rule is None:
        raise PricingRuleNotFoundError(f"Global pricing rule {rule_id} not found")
    return _enrich_global_rule(db, rule)


@rules_router.patch(
    "/global/{rule_id}",
    response_model=GlobalRuleRead,
    dependencies=[Depends(require_admin)],
)
def update_global_rule(
    rule_id: int,
    payload: GlobalRuleUpdate,
    db: Annotated[Session, Depends(get_db)],
) -> GlobalRuleRead:
    rule = pricing_rule_repository.get_global_rule(db, rule_id)
    if rule is None:
        raise PricingRuleNotFoundError(f"Global pricing rule {rule_id} not found")
    updates = payload.model_dump(exclude_unset=True)
    pricing_rule_repository.update_global_rule(db, rule, **updates)
    db.commit()
    db.refresh(rule)
    return _enrich_global_rule(db, rule)


@rules_router.delete(
    "/global/{rule_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_admin)],
)
def delete_global_rule(
    rule_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> None:
    pricing_rule_repository.delete_global_rule(db, rule_id)
    db.commit()


@rules_router.post(
    "/global/{rule_id}/duplicate",
    response_model=GlobalRuleRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)],
)
def duplicate_global_rule(
    rule_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> GlobalRuleRead:
    rule = pricing_rule_service.duplicate_rule(db, rule_id, rule_type="global")
    db.commit()
    db.refresh(rule)
    return _enrich_global_rule(db, rule)


# ---- Stage Rules ----


@rules_router.get(
    "/stage",
    response_model=list[StageRuleRead],
    dependencies=[Depends(require_admin)],
)
def list_stage_rules(
    estate_id: int = Query(...),
    stage_id: int = Query(...),
    db: Session = Depends(get_db),
) -> list[StageRuleRead]:
    rules = pricing_rule_repository.list_stage_rules(db, estate_id, stage_id)
    return [_enrich_stage_rule(db, r) for r in rules]


@rules_router.post(
    "/stage",
    response_model=StageRuleRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)],
)
def create_stage_rule(
    payload: StageRuleCreate,
    db: Annotated[Session, Depends(get_db)],
) -> StageRuleRead:
    # Validate estate and stage exist
    if estate_repository.get(db, payload.estate_id) is None:
        raise NotFoundError(f"Estate {payload.estate_id} not found")
    if stage_repository.get(db, payload.stage_id) is None:
        raise NotFoundError(f"Stage {payload.stage_id} not found")
    rule = pricing_rule_repository.create_stage_rule(
        db, **payload.model_dump()
    )
    db.commit()
    db.refresh(rule)
    return _enrich_stage_rule(db, rule)


@rules_router.get(
    "/stage/{rule_id}",
    response_model=StageRuleRead,
    dependencies=[Depends(require_admin)],
)
def get_stage_rule(
    rule_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> StageRuleRead:
    rule = pricing_rule_repository.get_stage_rule(db, rule_id)
    if rule is None:
        raise PricingRuleNotFoundError(f"Stage pricing rule {rule_id} not found")
    return _enrich_stage_rule(db, rule)


@rules_router.patch(
    "/stage/{rule_id}",
    response_model=StageRuleRead,
    dependencies=[Depends(require_admin)],
)
def update_stage_rule(
    rule_id: int,
    payload: StageRuleUpdate,
    db: Annotated[Session, Depends(get_db)],
) -> StageRuleRead:
    rule = pricing_rule_repository.get_stage_rule(db, rule_id)
    if rule is None:
        raise PricingRuleNotFoundError(f"Stage pricing rule {rule_id} not found")
    updates = payload.model_dump(exclude_unset=True)
    pricing_rule_repository.update_stage_rule(db, rule, **updates)
    db.commit()
    db.refresh(rule)
    return _enrich_stage_rule(db, rule)


@rules_router.delete(
    "/stage/{rule_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_admin)],
)
def delete_stage_rule(
    rule_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> None:
    pricing_rule_repository.delete_stage_rule(db, rule_id)
    db.commit()


@rules_router.post(
    "/stage/{rule_id}/duplicate",
    response_model=StageRuleRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)],
)
def duplicate_stage_rule(
    rule_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> StageRuleRead:
    rule = pricing_rule_service.duplicate_rule(db, rule_id, rule_type="stage")
    db.commit()
    db.refresh(rule)
    return _enrich_stage_rule(db, rule)

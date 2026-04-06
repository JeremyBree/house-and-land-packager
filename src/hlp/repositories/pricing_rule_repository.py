"""Pricing rule and category data access."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from hlp.models.pricing_rule import GlobalPricingRule, StagePricingRule
from hlp.models.pricing_rule_category import PricingRuleCategory

# --- Categories ---


def list_categories(db: Session, brand: str) -> list[PricingRuleCategory]:
    stmt = (
        select(PricingRuleCategory)
        .where(PricingRuleCategory.brand == brand)
        .order_by(PricingRuleCategory.sort_order, PricingRuleCategory.name)
    )
    return list(db.execute(stmt).scalars().all())


def get_category(db: Session, category_id: int) -> PricingRuleCategory | None:
    return db.get(PricingRuleCategory, category_id)


def create_category(db: Session, **fields) -> PricingRuleCategory:
    cat = PricingRuleCategory(**fields)
    db.add(cat)
    db.flush()
    return cat


def update_category(
    db: Session, category: PricingRuleCategory, **fields
) -> PricingRuleCategory:
    for key, value in fields.items():
        if value is not None:
            setattr(category, key, value)
    db.flush()
    return category


def delete_category(db: Session, category_id: int) -> None:
    cat = get_category(db, category_id)
    if cat is None:
        from hlp.shared.exceptions import CategoryNotFoundError

        raise CategoryNotFoundError(f"Category {category_id} not found")
    db.delete(cat)
    db.flush()


# --- Global Rules ---


def list_global_rules(db: Session, brand: str) -> list[GlobalPricingRule]:
    stmt = (
        select(GlobalPricingRule)
        .where(GlobalPricingRule.brand == brand)
        .order_by(GlobalPricingRule.sort_order, GlobalPricingRule.rule_id)
    )
    return list(db.execute(stmt).scalars().all())


def get_global_rule(db: Session, rule_id: int) -> GlobalPricingRule | None:
    return db.get(GlobalPricingRule, rule_id)


def create_global_rule(db: Session, **fields) -> GlobalPricingRule:
    rule = GlobalPricingRule(**fields)
    db.add(rule)
    db.flush()
    return rule


def update_global_rule(
    db: Session, rule: GlobalPricingRule, **fields
) -> GlobalPricingRule:
    for key, value in fields.items():
        if value is not None:
            setattr(rule, key, value)
    db.flush()
    return rule


def delete_global_rule(db: Session, rule_id: int) -> None:
    rule = get_global_rule(db, rule_id)
    if rule is None:
        from hlp.shared.exceptions import PricingRuleNotFoundError

        raise PricingRuleNotFoundError(f"Global pricing rule {rule_id} not found")
    db.delete(rule)
    db.flush()


# --- Stage Rules ---


def list_stage_rules(
    db: Session, estate_id: int, stage_id: int
) -> list[StagePricingRule]:
    stmt = (
        select(StagePricingRule)
        .where(
            StagePricingRule.estate_id == estate_id,
            StagePricingRule.stage_id == stage_id,
        )
        .order_by(StagePricingRule.sort_order, StagePricingRule.rule_id)
    )
    return list(db.execute(stmt).scalars().all())


def get_stage_rule(db: Session, rule_id: int) -> StagePricingRule | None:
    return db.get(StagePricingRule, rule_id)


def create_stage_rule(db: Session, **fields) -> StagePricingRule:
    rule = StagePricingRule(**fields)
    db.add(rule)
    db.flush()
    return rule


def update_stage_rule(
    db: Session, rule: StagePricingRule, **fields
) -> StagePricingRule:
    for key, value in fields.items():
        if value is not None:
            setattr(rule, key, value)
    db.flush()
    return rule


def delete_stage_rule(db: Session, rule_id: int) -> None:
    rule = get_stage_rule(db, rule_id)
    if rule is None:
        from hlp.shared.exceptions import PricingRuleNotFoundError

        raise PricingRuleNotFoundError(f"Stage pricing rule {rule_id} not found")
    db.delete(rule)
    db.flush()

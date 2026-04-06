"""Pricing rule service: condition evaluation, duplication."""

from __future__ import annotations

import logging
from typing import Any

from sqlalchemy.orm import Session

from hlp.models.pricing_rule import GlobalPricingRule, StagePricingRule
from hlp.repositories import pricing_rule_repository
from hlp.shared.exceptions import PricingRuleNotFoundError

logger = logging.getLogger(__name__)

# Boolean conditions — the rule applies when context[key] is truthy
_BOOLEAN_CONDITIONS = frozenset({
    "corner_block",
    "building_crossover",
    "is_kdrb",
    "is_10_90_deal",
    "developer_land_referrals",
    "custom_house_design",
})


def _evaluate_condition(condition: str | None, context: dict[str, Any]) -> bool:
    """Return True if a rule's condition is satisfied by the given context.

    - No condition → always included.
    - Boolean condition (e.g. "corner_block") → context["corner_block"] == True.
    - Keyed condition "house_type:{value}" → value in context["house_types"].
    - Keyed condition "wholesale_group:{value}" → context["wholesale_group"] == value.
    - Unknown condition → excluded (fail-safe).
    """
    if not condition:
        return True

    # Check boolean conditions
    if condition in _BOOLEAN_CONDITIONS:
        return bool(context.get(condition))

    # Check keyed conditions (key:value)
    if ":" in condition:
        key, _, value = condition.partition(":")
        if key == "house_type":
            house_types = context.get("house_types", [])
            return value in house_types
        if key == "wholesale_group":
            return context.get("wholesale_group") == value

    # Unknown condition → excluded
    logger.warning("Unknown pricing rule condition: %s", condition)
    return False


def evaluate_rules(
    rules: list[GlobalPricingRule | StagePricingRule],
    context: dict[str, Any],
) -> list[GlobalPricingRule | StagePricingRule]:
    """Filter rules to only those whose conditions match the given context."""
    return [r for r in rules if _evaluate_condition(r.condition, context)]


def duplicate_rule(
    db: Session,
    source_rule_id: int,
    rule_type: str = "global",
) -> GlobalPricingRule | StagePricingRule:
    """Duplicate a pricing rule (global or stage) into a new rule with the same fields."""
    if rule_type == "global":
        source = pricing_rule_repository.get_global_rule(db, source_rule_id)
        if source is None:
            raise PricingRuleNotFoundError(
                f"Global pricing rule {source_rule_id} not found"
            )
        return pricing_rule_repository.create_global_rule(
            db,
            brand=source.brand,
            item_name=source.item_name,
            cost=source.cost,
            condition=source.condition,
            condition_value=source.condition_value,
            cell_row=source.cell_row,
            cell_col=source.cell_col,
            cost_cell_row=source.cost_cell_row,
            cost_cell_col=source.cost_cell_col,
            category_id=source.category_id,
            sort_order=source.sort_order,
        )

    if rule_type == "stage":
        source = pricing_rule_repository.get_stage_rule(db, source_rule_id)
        if source is None:
            raise PricingRuleNotFoundError(
                f"Stage pricing rule {source_rule_id} not found"
            )
        return pricing_rule_repository.create_stage_rule(
            db,
            estate_id=source.estate_id,
            stage_id=source.stage_id,
            brand=source.brand,
            item_name=source.item_name,
            cost=source.cost,
            condition=source.condition,
            condition_value=source.condition_value,
            cell_row=source.cell_row,
            cell_col=source.cell_col,
            cost_cell_row=source.cost_cell_row,
            cost_cell_col=source.cost_cell_col,
            category_id=source.category_id,
            sort_order=source.sort_order,
        )

    raise ValueError(f"Invalid rule_type: {rule_type}. Must be 'global' or 'stage'.")

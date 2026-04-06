"""Unit tests for hlp.shared.pricing_rule_service condition evaluation DSL."""
from __future__ import annotations

from decimal import Decimal

from hlp.models.pricing_rule import GlobalPricingRule
from hlp.shared import pricing_rule_service


def _make_rule(
    condition: str | None = None,
    condition_value: str | None = None,
    item_name: str = "Test Item",
) -> GlobalPricingRule:
    """Create an in-memory GlobalPricingRule (no DB round-trip needed)."""
    rule = GlobalPricingRule(
        brand="Hermitage Homes",
        item_name=item_name,
        cost=Decimal("100.00"),
        condition=condition,
        condition_value=condition_value,
        cell_row=1,
        cell_col=1,
        cost_cell_row=1,
        cost_cell_col=2,
        sort_order=0,
    )
    return rule


# --- Test: no condition → always included ---


def test_evaluate_rules_no_condition_always_included():
    rule = _make_rule(condition=None)
    result = pricing_rule_service.evaluate_rules([rule], {})
    assert result == [rule]


# --- Test: corner_block true → includes rule ---


def test_evaluate_rules_corner_block_true_includes_rule():
    rule = _make_rule(condition="corner_block")
    ctx = {"corner_block": True}
    result = pricing_rule_service.evaluate_rules([rule], ctx)
    assert result == [rule]


# --- Test: corner_block false → excludes rule ---


def test_evaluate_rules_corner_block_false_excludes_rule():
    rule = _make_rule(condition="corner_block")
    ctx = {"corner_block": False}
    result = pricing_rule_service.evaluate_rules([rule], ctx)
    assert result == []


# --- Test: building_crossover true ---


def test_evaluate_rules_building_crossover_true():
    rule = _make_rule(condition="building_crossover")
    ctx = {"building_crossover": True}
    result = pricing_rule_service.evaluate_rules([rule], ctx)
    assert result == [rule]


# --- Test: is_kdrb ---


def test_evaluate_rules_is_kdrb():
    rule = _make_rule(condition="is_kdrb")
    ctx = {"is_kdrb": True}
    result = pricing_rule_service.evaluate_rules([rule], ctx)
    assert result == [rule]

    result_false = pricing_rule_service.evaluate_rules([rule], {"is_kdrb": False})
    assert result_false == []


# --- Test: house_type match ---


def test_evaluate_rules_house_type_match():
    rule = _make_rule(condition="house_type:Access 18")
    ctx = {"house_types": ["Access 18", "Camden 25"]}
    result = pricing_rule_service.evaluate_rules([rule], ctx)
    assert result == [rule]


# --- Test: house_type no match ---


def test_evaluate_rules_house_type_no_match():
    rule = _make_rule(condition="house_type:Alpine 30")
    ctx = {"house_types": ["Access 18", "Camden 25"]}
    result = pricing_rule_service.evaluate_rules([rule], ctx)
    assert result == []


# --- Test: wholesale_group match ---


def test_evaluate_rules_wholesale_group_match():
    rule = _make_rule(condition="wholesale_group:GroupA")
    ctx = {"wholesale_group": "GroupA"}
    result = pricing_rule_service.evaluate_rules([rule], ctx)
    assert result == [rule]


# --- Test: unknown condition → excluded ---


def test_evaluate_rules_unknown_condition_excluded():
    rule = _make_rule(condition="some_future_condition")
    result = pricing_rule_service.evaluate_rules([rule], {})
    assert result == []


# --- Test: multiple conditions mixed ---


def test_evaluate_rules_multiple_conditions_mixed():
    always_rule = _make_rule(condition=None, item_name="Always")
    corner_rule = _make_rule(condition="corner_block", item_name="Corner")
    kdrb_rule = _make_rule(condition="is_kdrb", item_name="KDRB")
    house_rule = _make_rule(condition="house_type:Access 18", item_name="House")

    all_rules = [always_rule, corner_rule, kdrb_rule, house_rule]
    ctx = {
        "corner_block": True,
        "is_kdrb": False,
        "house_types": ["Access 18"],
    }
    result = pricing_rule_service.evaluate_rules(all_rules, ctx)
    # always_rule: included (no condition)
    # corner_rule: included (corner_block=True)
    # kdrb_rule: excluded (is_kdrb=False)
    # house_rule: included (Access 18 in house_types)
    assert len(result) == 3
    assert always_rule in result
    assert corner_rule in result
    assert house_rule in result
    assert kdrb_rule not in result

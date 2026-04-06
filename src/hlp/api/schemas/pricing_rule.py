"""Pricing rule and category request/response schemas."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

# --- Categories ---


class RuleCategoryCreate(BaseModel):
    name: str
    brand: str
    sort_order: int = 0


class RuleCategoryUpdate(BaseModel):
    name: str | None = None
    sort_order: int | None = None


class RuleCategoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    category_id: int
    name: str
    brand: str
    sort_order: int


# --- Global Rules ---


class GlobalRuleCreate(BaseModel):
    brand: str
    item_name: str
    cost: Decimal
    condition: str | None = None
    condition_value: str | None = None
    cell_row: int
    cell_col: int
    cost_cell_row: int
    cost_cell_col: int
    category_id: int | None = None
    sort_order: int = 0


class GlobalRuleUpdate(BaseModel):
    brand: str | None = None
    item_name: str | None = None
    cost: Decimal | None = None
    condition: str | None = None
    condition_value: str | None = None
    cell_row: int | None = None
    cell_col: int | None = None
    cost_cell_row: int | None = None
    cost_cell_col: int | None = None
    category_id: int | None = None
    sort_order: int | None = None


class GlobalRuleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    rule_id: int
    brand: str
    item_name: str
    cost: Decimal
    condition: str | None
    condition_value: str | None
    cell_row: int
    cell_col: int
    cost_cell_row: int
    cost_cell_col: int
    category_id: int | None
    sort_order: int
    created_at: datetime
    updated_at: datetime
    category_name: str | None = None


# --- Stage Rules ---


class StageRuleCreate(BaseModel):
    estate_id: int
    stage_id: int
    brand: str
    item_name: str
    cost: Decimal
    condition: str | None = None
    condition_value: str | None = None
    cell_row: int
    cell_col: int
    cost_cell_row: int
    cost_cell_col: int
    category_id: int | None = None
    sort_order: int = 0


class StageRuleUpdate(BaseModel):
    brand: str | None = None
    item_name: str | None = None
    cost: Decimal | None = None
    condition: str | None = None
    condition_value: str | None = None
    cell_row: int | None = None
    cell_col: int | None = None
    cost_cell_row: int | None = None
    cost_cell_col: int | None = None
    category_id: int | None = None
    sort_order: int | None = None


class StageRuleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    rule_id: int
    estate_id: int
    stage_id: int
    brand: str
    item_name: str
    cost: Decimal
    condition: str | None
    condition_value: str | None
    cell_row: int
    cell_col: int
    cost_cell_row: int
    cost_cell_col: int
    category_id: int | None
    sort_order: int
    created_at: datetime
    updated_at: datetime
    estate_name: str | None = None
    stage_name: str | None = None
    category_name: str | None = None


# --- Duplicate ---


class RuleDuplicateRequest(BaseModel):
    source_rule_id: int

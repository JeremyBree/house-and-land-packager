"""Pricing engine API schemas."""

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class LotPricingInputSchema(BaseModel):
    lot_number: str
    lot_frontage: Decimal
    lot_depth: Decimal
    lot_size_sqm: Decimal
    land_price: Decimal
    corner_block: bool = False
    orientation: str = "N"
    house_name: str
    facade_name: str
    garage_side: str = "Left"
    fall_mm: int = 0
    fill_trees: bool = False
    easement_proximity_lhs: bool = False
    easement_proximity_rhs: bool = False
    retaining_lhs: bool = False
    retaining_rhs: bool = False


class PricingContextSchema(BaseModel):
    estate_id: int
    stage_id: int
    brand: str
    suburb: str
    postcode: str
    bdm_profile_id: int | None = None
    wholesale_group_name: str | None = None
    is_kdrb: bool = False
    is_10_90_deal: bool = False
    holding_costs_apply: bool = False
    developer_land_referrals: bool = False
    building_crossover: bool = False
    shared_crossovers: bool = False
    pricing_date: date = Field(default_factory=date.today)
    contract_date: date | None = None


class PricingCalculateRequest(BaseModel):
    context: PricingContextSchema
    lots: list[LotPricingInputSchema]


class PriceLineItemResponse(BaseModel):
    name: str
    amount: str
    category: str
    detail: str | None = None


class PriceBreakdownResponse(BaseModel):
    lot_number: str
    house_name: str
    facade_name: str
    house_price: str
    facade_price: str
    energy_compliance_cost: str
    site_costs_total: str
    design_guidelines_total: str
    extra_landscaping: str
    extra_landscaping_sqm: str
    upgrades_total: str
    discount: str
    discount_reason: str | None = None
    kdrb_surcharge: str
    fbc_escalation_pct: str
    fbc_escalation_amount: str
    holding_costs: str
    commission_fixed: str | None = None
    commission_pct: str | None = None
    comms_adjustment: str
    total_build_price: str
    total_package_price: str
    land_price: str
    house_fits: bool
    house_fits_reason: str | None = None
    extra_fence_meterage: str
    line_items: list[PriceLineItemResponse] = []
    warnings: list[str] = []

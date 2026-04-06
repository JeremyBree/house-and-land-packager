"""PricingConfig API schemas."""

from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class PricingConfigRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    config_id: int
    brand: str
    landscaping_rate_per_sqm: Decimal
    base_commission: Decimal
    pct_commission_divisor: Decimal
    kdrb_surcharge: Decimal
    holding_cost_rate: Decimal
    small_lot_threshold_sqm: Decimal
    small_lot_discount: Decimal
    dwellings_discount: Decimal
    corner_block_savings: Decimal
    build_price_rounding: int
    package_price_rounding: int


class PricingConfigUpdate(BaseModel):
    landscaping_rate_per_sqm: Decimal | None = None
    base_commission: Decimal | None = None
    pct_commission_divisor: Decimal | None = None
    kdrb_surcharge: Decimal | None = None
    holding_cost_rate: Decimal | None = None
    small_lot_threshold_sqm: Decimal | None = None
    small_lot_discount: Decimal | None = None
    dwellings_discount: Decimal | None = None
    corner_block_savings: Decimal | None = None
    build_price_rounding: int | None = None
    package_price_rounding: int | None = None

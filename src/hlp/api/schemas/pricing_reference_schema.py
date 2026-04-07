"""Pricing reference data schemas — travel surcharges, site costs, postcode costs, FBC bands."""

from pydantic import BaseModel, ConfigDict, Field


# ── Travel Surcharges ──────────────────────────────────────────────

class TravelSurchargeCreate(BaseModel):
    suburb_name: str = Field(min_length=1, max_length=100)
    postcode: str | None = Field(default=None, max_length=10)
    surcharge_amount: float
    region_name: str | None = Field(default=None, max_length=50)


class TravelSurchargeUpdate(BaseModel):
    suburb_name: str | None = Field(default=None, max_length=100)
    postcode: str | None = None
    surcharge_amount: float | None = None
    region_name: str | None = None


class TravelSurchargeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    surcharge_id: int
    suburb_name: str
    postcode: str | None = None
    surcharge_amount: float
    region_name: str | None = None


# ── Site Cost Tiers ────────────────────────────────────────────────

class SiteCostTierCreate(BaseModel):
    tier_name: str = Field(min_length=1, max_length=50)
    fall_min_mm: int
    fall_max_mm: int


class SiteCostTierUpdate(BaseModel):
    tier_name: str | None = Field(default=None, max_length=50)
    fall_min_mm: int | None = None
    fall_max_mm: int | None = None


class SiteCostTierRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    tier_id: int
    tier_name: str
    fall_min_mm: int
    fall_max_mm: int


# ── Site Cost Items ────────────────────────────────────────────────

class SiteCostItemCreate(BaseModel):
    tier_id: int | None = None
    item_name: str = Field(min_length=1, max_length=255)
    condition_type: str | None = Field(default=None, max_length=100)
    condition_description: str | None = None
    cost_single_lt190: float | None = None
    cost_double_lt190: float | None = None
    cost_single_191_249: float | None = None
    cost_double_191_249: float | None = None
    cost_single_250_300: float | None = None
    cost_double_250_300: float | None = None
    cost_single_300plus: float | None = None
    cost_double_300plus: float | None = None
    sort_order: int = 0


class SiteCostItemUpdate(BaseModel):
    tier_id: int | None = None
    item_name: str | None = Field(default=None, max_length=255)
    condition_type: str | None = None
    condition_description: str | None = None
    cost_single_lt190: float | None = None
    cost_double_lt190: float | None = None
    cost_single_191_249: float | None = None
    cost_double_191_249: float | None = None
    cost_single_250_300: float | None = None
    cost_double_250_300: float | None = None
    cost_single_300plus: float | None = None
    cost_double_300plus: float | None = None
    sort_order: int | None = None


class SiteCostItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    item_id: int
    tier_id: int | None = None
    item_name: str
    condition_type: str | None = None
    condition_description: str | None = None
    cost_single_lt190: float | None = None
    cost_double_lt190: float | None = None
    cost_single_191_249: float | None = None
    cost_double_191_249: float | None = None
    cost_single_250_300: float | None = None
    cost_double_250_300: float | None = None
    cost_single_300plus: float | None = None
    cost_double_300plus: float | None = None
    sort_order: int


# ── Postcode Site Costs ────────────────────────────────────────────

class PostcodeSiteCostCreate(BaseModel):
    postcode: str = Field(min_length=1, max_length=10)
    rock_removal_cost: float


class PostcodeSiteCostUpdate(BaseModel):
    rock_removal_cost: float | None = None


class PostcodeSiteCostRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    postcode: str
    rock_removal_cost: float


# ── FBC Escalation Bands ──────────────────────────────────────────

class FbcEscalationBandCreate(BaseModel):
    brand: str = Field(min_length=1, max_length=100)
    day_start: int
    day_end: int
    multiplier: float


class FbcEscalationBandUpdate(BaseModel):
    brand: str | None = Field(default=None, max_length=100)
    day_start: int | None = None
    day_end: int | None = None
    multiplier: float | None = None


class FbcEscalationBandRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    band_id: int
    brand: str
    day_start: int
    day_end: int
    multiplier: float

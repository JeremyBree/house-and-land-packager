"""House design and facade API schemas."""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class HouseFacadeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    facade_id: int
    design_id: int
    facade_name: str
    facade_price: float
    facade_details: str | None = None
    is_included: bool


class EnergyRatingRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    rating_id: int
    design_id: int
    garage_side: str
    orientation: str
    star_rating: float
    best_worst: str
    compliance_cost: float


class HouseDesignRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    design_id: int
    brand: str
    house_name: str
    base_price: float
    storey: str
    frontage: float
    depth: float
    gf_sqm: float
    total_sqm: float
    lot_total_sqm: float
    squares: int
    details: str | None = None
    effective_date: date | None = None
    active: bool
    facades: list[HouseFacadeRead] = []


class HouseDesignDetailRead(HouseDesignRead):
    energy_ratings: list[EnergyRatingRead] = []

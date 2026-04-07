"""House design and facade API schemas."""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class HouseFacadeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    facade_id: int
    design_id: int
    facade_name: str
    facade_price: float
    facade_details: str | None = None
    is_included: bool


class HouseFacadeCreate(BaseModel):
    facade_name: str = Field(min_length=1, max_length=100)
    facade_price: float = Field(default=0, ge=0)
    facade_details: str | None = None
    is_included: bool = False


class HouseFacadeUpdate(BaseModel):
    facade_name: str | None = Field(default=None, min_length=1, max_length=100)
    facade_price: float | None = Field(default=None, ge=0)
    facade_details: str | None = None
    is_included: bool | None = None


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


class HouseDesignCreate(BaseModel):
    brand: str = Field(min_length=1, max_length=100)
    house_name: str = Field(min_length=1, max_length=100)
    base_price: float = Field(ge=0)
    storey: str = Field(min_length=1, max_length=10)
    frontage: float = Field(ge=0)
    depth: float = Field(ge=0)
    gf_sqm: float = Field(ge=0)
    total_sqm: float = Field(ge=0)
    lot_total_sqm: float = Field(ge=0)
    squares: int = Field(ge=0)
    details: str | None = None
    effective_date: date | None = None
    active: bool = True


class HouseDesignUpdate(BaseModel):
    brand: str | None = Field(default=None, min_length=1, max_length=100)
    house_name: str | None = Field(default=None, min_length=1, max_length=100)
    base_price: float | None = Field(default=None, ge=0)
    storey: str | None = Field(default=None, min_length=1, max_length=10)
    frontage: float | None = Field(default=None, ge=0)
    depth: float | None = Field(default=None, ge=0)
    gf_sqm: float | None = Field(default=None, ge=0)
    total_sqm: float | None = Field(default=None, ge=0)
    lot_total_sqm: float | None = Field(default=None, ge=0)
    squares: int | None = Field(default=None, ge=0)
    details: str | None = None
    effective_date: date | None = None
    active: bool | None = None


class EnergyRatingCreate(BaseModel):
    garage_side: str = Field(min_length=1, max_length=10)
    orientation: str = Field(min_length=1, max_length=5)
    star_rating: float = Field(ge=0)
    best_worst: str = Field(min_length=1, max_length=1)
    compliance_cost: float = Field(ge=0)


class EnergyRatingUpdate(BaseModel):
    garage_side: str | None = Field(default=None, min_length=1, max_length=10)
    orientation: str | None = Field(default=None, min_length=1, max_length=5)
    star_rating: float | None = Field(default=None, ge=0)
    best_worst: str | None = Field(default=None, min_length=1, max_length=1)
    compliance_cost: float | None = Field(default=None, ge=0)


class HouseDesignDetailRead(HouseDesignRead):
    energy_ratings: list[EnergyRatingRead] = []

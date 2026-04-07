"""External ingestion request/response schemas."""

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field


# ---- Estate upsert ----

class EstateUpsertInput(BaseModel):
    estate_name: str = Field(min_length=1, max_length=255)
    suburb: str | None = Field(default=None, max_length=255)
    postcode: str | None = Field(default=None, max_length=10)
    developer_name: str = Field(min_length=1, max_length=255)
    region_name: str | None = Field(default=None, max_length=255)
    contact_name: str | None = Field(default=None, max_length=255)
    contact_email: str | None = Field(default=None, max_length=255)
    contact_mobile: str | None = Field(default=None, max_length=50)


class EstateUpsertResponse(BaseModel):
    estate_id: int
    estate_name: str
    action: str  # "created" or "updated"


# ---- Stage upsert ----

class StageUpsertInput(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    lot_count: int | None = None
    status: str | None = None
    release_date: date | None = None


class StageUpsertResponse(BaseModel):
    stage_id: int
    name: str
    action: str


# ---- Lot bulk upsert ----

class LotUpsertItem(BaseModel):
    lot_number: str = Field(min_length=1, max_length=50)
    street_name: str | None = Field(default=None, max_length=255)
    frontage: Decimal | None = None
    depth: Decimal | None = None
    size_sqm: Decimal | None = None
    land_price: Decimal | None = None
    orientation: str | None = Field(default=None, max_length=20)
    corner_block: bool | None = None


class LotBulkUpsertInput(BaseModel):
    lots: list[LotUpsertItem] = Field(min_length=1)


class LotBulkUpsertResponse(BaseModel):
    created: int
    updated: int
    total: int


# ---- Guideline upsert ----

class GuidelineUpsertItem(BaseModel):
    guideline_type: str = Field(min_length=1, max_length=100)
    cost: float | None = None
    override_text: str | None = None


class GuidelineUpsertInput(BaseModel):
    stage_id: int | None = None
    guidelines: list[GuidelineUpsertItem] = Field(min_length=1)


class GuidelineUpsertResponse(BaseModel):
    created: int
    updated: int

"""Stage lot request/response schemas."""

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from hlp.models.enums import LotStatus, Source


class LotCreate(BaseModel):
    lot_number: str = Field(min_length=1, max_length=50)
    frontage: Decimal | None = None
    depth: Decimal | None = None
    size_sqm: Decimal | None = None
    corner_block: bool = False
    orientation: str | None = Field(default=None, max_length=20)
    side_easement: Decimal | None = None
    rear_easement: Decimal | None = None
    street_name: str | None = Field(default=None, max_length=255)
    land_price: Decimal | None = None
    build_price: Decimal | None = None
    package_price: Decimal | None = None
    substation: bool = False
    title_date: date | None = None


class LotUpdate(BaseModel):
    lot_number: str | None = Field(default=None, min_length=1, max_length=50)
    frontage: Decimal | None = None
    depth: Decimal | None = None
    size_sqm: Decimal | None = None
    corner_block: bool | None = None
    orientation: str | None = Field(default=None, max_length=20)
    side_easement: Decimal | None = None
    rear_easement: Decimal | None = None
    street_name: str | None = Field(default=None, max_length=255)
    land_price: Decimal | None = None
    build_price: Decimal | None = None
    package_price: Decimal | None = None
    substation: bool | None = None
    title_date: date | None = None


class LotRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    lot_id: int
    stage_id: int
    lot_number: str
    frontage: Decimal | None = None
    depth: Decimal | None = None
    size_sqm: Decimal | None = None
    corner_block: bool
    orientation: str | None = None
    side_easement: Decimal | None = None
    rear_easement: Decimal | None = None
    street_name: str | None = None
    land_price: Decimal | None = None
    build_price: Decimal | None = None
    package_price: Decimal | None = None
    status: LotStatus
    substation: bool
    title_date: date | None = None
    last_confirmed_date: datetime | None = None
    source: Source | None = None
    created_at: datetime
    updated_at: datetime


class LotBulkCreate(BaseModel):
    lots: list[LotCreate]


class LotStatusTransition(BaseModel):
    new_status: LotStatus
    reason: str = Field(min_length=1, max_length=500)


class StatusHistoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    history_id: int
    lot_id: int
    previous_status: LotStatus | None = None
    new_status: LotStatus
    changed_at: datetime
    triggering_agent: str
    source_detail: str | None = None


class CsvRowError(BaseModel):
    row: int
    error: str


class CsvUploadResult(BaseModel):
    created: int
    skipped: int
    errors: list[CsvRowError] = Field(default_factory=list)

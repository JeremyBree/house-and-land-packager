"""HousePackage request/response schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PackageCreate(BaseModel):
    estate_id: int
    stage_id: int
    lot_number: str = Field(min_length=1, max_length=50)
    design: str = Field(min_length=1, max_length=255)
    facade: str = Field(min_length=1, max_length=255)
    colour_scheme: str | None = Field(default=None, max_length=255)
    brand: str = Field(min_length=1, max_length=100)
    source: str | None = Field(default=None, max_length=500)
    status: str | None = Field(default=None, max_length=50)


class PackageUpdate(BaseModel):
    estate_id: int | None = None
    stage_id: int | None = None
    lot_number: str | None = Field(default=None, min_length=1, max_length=50)
    design: str | None = Field(default=None, min_length=1, max_length=255)
    facade: str | None = Field(default=None, min_length=1, max_length=255)
    colour_scheme: str | None = Field(default=None, max_length=255)
    brand: str | None = Field(default=None, min_length=1, max_length=100)
    source: str | None = Field(default=None, max_length=500)
    status: str | None = Field(default=None, max_length=50)


class PackageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    package_id: int
    estate_id: int
    stage_id: int
    lot_number: str
    design: str
    facade: str
    colour_scheme: str | None = None
    brand: str
    source: str | None = None
    status: str | None = None
    flyer_path: str | None = None
    created_at: datetime
    updated_at: datetime


class PackageDetailRead(PackageRead):
    estate_name: str | None = None
    stage_name: str | None = None
    lot_id: int | None = None


class PackageListQuery(BaseModel):
    estate_id: int | None = None
    stage_id: int | None = None
    brand: str | None = None
    design: str | None = None
    facade: str | None = None
    lot_number: str | None = None
    page: int = Field(default=1, ge=1)
    size: int = Field(default=25, ge=1, le=200)

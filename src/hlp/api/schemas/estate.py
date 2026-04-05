"""Estate request/response schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from hlp.api.schemas.developer import DeveloperRead
from hlp.api.schemas.region import RegionRead


class EstateCreate(BaseModel):
    developer_id: int
    region_id: int | None = None
    estate_name: str = Field(min_length=1, max_length=255)
    suburb: str | None = Field(default=None, max_length=255)
    state: str | None = Field(default=None, max_length=10)
    postcode: str | None = Field(default=None, max_length=10)
    contact_name: str | None = Field(default=None, max_length=255)
    contact_mobile: str | None = Field(default=None, max_length=50)
    contact_email: EmailStr | None = None
    description: str | None = None
    notes: str | None = None


class EstateUpdate(BaseModel):
    developer_id: int | None = None
    region_id: int | None = None
    estate_name: str | None = Field(default=None, min_length=1, max_length=255)
    suburb: str | None = Field(default=None, max_length=255)
    state: str | None = Field(default=None, max_length=10)
    postcode: str | None = Field(default=None, max_length=10)
    contact_name: str | None = Field(default=None, max_length=255)
    contact_mobile: str | None = Field(default=None, max_length=50)
    contact_email: EmailStr | None = None
    description: str | None = None
    notes: str | None = None
    active: bool | None = None


class EstateRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    estate_id: int
    developer_id: int
    region_id: int | None = None
    estate_name: str
    suburb: str | None = None
    state: str | None = None
    postcode: str | None = None
    contact_name: str | None = None
    contact_mobile: str | None = None
    contact_email: str | None = None
    description: str | None = None
    notes: str | None = None
    active: bool
    created_at: datetime
    updated_at: datetime


class EstateDetailRead(EstateRead):
    developer: DeveloperRead
    region: RegionRead | None = None
    stages_count: int = 0

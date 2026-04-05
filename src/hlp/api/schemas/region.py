"""Region request/response schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class RegionCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)


class RegionUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=255)


class RegionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    region_id: int
    name: str
    created_at: datetime

"""Filter preset request/response schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from hlp.api.schemas.lot_search import LotSearchFilters


class FilterPresetCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    filters: LotSearchFilters


class FilterPresetUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    filters: LotSearchFilters | None = None


class FilterPresetRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    preset_id: int
    profile_id: int
    name: str
    filters: dict
    created_at: datetime
    updated_at: datetime

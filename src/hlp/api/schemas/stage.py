"""Estate stage request/response schemas."""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from hlp.models.enums import StageStatus


class StageCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    lot_count: int | None = Field(default=None, ge=0)
    status: StageStatus = StageStatus.ACTIVE
    release_date: date | None = None


class StageUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    lot_count: int | None = Field(default=None, ge=0)
    status: StageStatus | None = None
    release_date: date | None = None


class StageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    stage_id: int
    estate_id: int
    name: str
    lot_count: int | None = None
    status: StageStatus
    release_date: date | None = None
    created_at: datetime
    updated_at: datetime


class StageDetailRead(StageRead):
    lot_count_actual: int = 0
    status_breakdown: dict[str, int] = Field(default_factory=dict)

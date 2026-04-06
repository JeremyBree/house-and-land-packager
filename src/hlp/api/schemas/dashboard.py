"""Dashboard response schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class RecentRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    request_id: int
    brand: str
    status: str
    estate_name: str | None = None
    stage_name: str | None = None
    lot_count: int = 0
    created_at: datetime


class DashboardRead(BaseModel):
    total_estates: int
    total_lots: int
    total_packages: int
    active_conflicts: int
    pending_requests: int
    lot_status_breakdown: dict[str, int]
    recent_requests: list[RecentRequest]

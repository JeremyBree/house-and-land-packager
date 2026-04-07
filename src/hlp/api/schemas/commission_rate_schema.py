"""Commission rate API schemas."""

from pydantic import BaseModel, ConfigDict


class CommissionRateRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    rate_id: int
    bdm_profile_id: int
    group_id: int
    commission_fixed: float | None = None
    commission_pct: float | None = None
    brand: str
    bdm_name: str | None = None
    group_name: str | None = None


class CommissionRateCreate(BaseModel):
    bdm_profile_id: int
    group_id: int
    brand: str
    commission_fixed: float | None = None
    commission_pct: float | None = None


class CommissionRateUpdate(BaseModel):
    commission_fixed: float | None = None
    commission_pct: float | None = None
    brand: str | None = None
    bdm_profile_id: int | None = None
    group_id: int | None = None

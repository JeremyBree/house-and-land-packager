"""Wholesale group API schemas."""

from pydantic import BaseModel, ConfigDict


class WholesaleGroupRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    group_id: int
    group_name: str
    gst_registered: bool
    active: bool


class WholesaleGroupCreate(BaseModel):
    group_name: str
    gst_registered: bool = False
    active: bool = True


class WholesaleGroupUpdate(BaseModel):
    group_name: str | None = None
    gst_registered: bool | None = None
    active: bool | None = None

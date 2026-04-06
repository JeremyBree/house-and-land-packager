"""Wholesale group API schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class WholesaleGroupRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    group_id: int
    group_name: str
    gst_registered: bool
    active: bool

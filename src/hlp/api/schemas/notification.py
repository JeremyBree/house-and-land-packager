"""Notification request/response schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class NotificationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    notification_id: int
    profile_id: int
    pricing_request_id: int
    title: str
    message: str
    read: bool
    created_at: datetime


class NotificationMarkRead(BaseModel):
    read: bool = True

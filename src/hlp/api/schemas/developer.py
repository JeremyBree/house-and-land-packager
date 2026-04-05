"""Developer request/response schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class DeveloperCreate(BaseModel):
    developer_name: str = Field(min_length=1, max_length=255)
    developer_website: str | None = Field(default=None, max_length=500)
    contact_email: EmailStr | None = None
    notes: str | None = None


class DeveloperUpdate(BaseModel):
    developer_name: str | None = Field(default=None, min_length=1, max_length=255)
    developer_website: str | None = Field(default=None, max_length=500)
    contact_email: EmailStr | None = None
    notes: str | None = None


class DeveloperRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    developer_id: int
    developer_name: str
    developer_website: str | None = None
    contact_email: str | None = None
    notes: str | None = None
    created_at: datetime
    updated_at: datetime

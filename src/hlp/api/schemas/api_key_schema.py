"""API key request/response schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ApiKeyCreateInput(BaseModel):
    agent_name: str = Field(min_length=1, max_length=100)
    agent_type: str = Field(min_length=1, max_length=50)
    scopes: str = Field(default="", max_length=500)
    expires_at: datetime | None = None
    notes: str | None = None


class ApiKeyUpdate(BaseModel):
    agent_name: str | None = Field(default=None, max_length=100)
    agent_type: str | None = Field(default=None, max_length=50)
    scopes: str | None = Field(default=None, max_length=500)
    is_active: bool | None = None
    notes: str | None = None


class ApiKeyRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    key_id: int
    key_prefix: str
    agent_name: str
    agent_type: str
    scopes: str
    is_active: bool
    last_used_at: datetime | None = None
    expires_at: datetime | None = None
    created_by: int
    notes: str | None = None
    created_at: datetime
    updated_at: datetime


class ApiKeyCreateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    key_id: int
    key_prefix: str
    agent_name: str
    agent_type: str
    scopes: str
    is_active: bool
    expires_at: datetime | None = None
    created_by: int
    notes: str | None = None
    created_at: datetime
    updated_at: datetime
    raw_key: str  # Only shown once at creation time

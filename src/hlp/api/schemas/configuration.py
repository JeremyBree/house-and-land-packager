"""Configuration request/response schemas."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ConfigurationCreate(BaseModel):
    config_type: str = Field(min_length=1, max_length=50)
    estate_id: int | None = None
    label: str = Field(min_length=1, max_length=255)
    url_or_path: str = Field(min_length=1, max_length=500)
    credentials_ref: str | None = Field(default=None, max_length=255)
    run_schedule: str | None = Field(default=None, max_length=100)
    enabled: bool = True
    priority_rank: int = 0
    notes: str | None = None
    scraping_config: dict[str, Any] = Field(default_factory=dict)


class ConfigurationUpdate(BaseModel):
    config_type: str | None = Field(default=None, max_length=50)
    estate_id: int | None = None
    label: str | None = Field(default=None, max_length=255)
    url_or_path: str | None = Field(default=None, max_length=500)
    credentials_ref: str | None = Field(default=None, max_length=255)
    run_schedule: str | None = Field(default=None, max_length=100)
    enabled: bool | None = None
    priority_rank: int | None = None
    notes: str | None = None
    scraping_config: dict[str, Any] | None = None


class ConfigurationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    config_id: int
    config_type: str
    estate_id: int | None = None
    label: str
    url_or_path: str
    credentials_ref: str | None = None
    run_schedule: str | None = None
    enabled: bool
    priority_rank: int
    notes: str | None = None
    scraping_config: dict[str, Any]
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, obj) -> "ConfigurationRead":
        """Create a read schema, masking credentials_ref."""
        data = {
            "config_id": obj.config_id,
            "config_type": obj.config_type.value if hasattr(obj.config_type, "value") else obj.config_type,
            "estate_id": obj.estate_id,
            "label": obj.label,
            "url_or_path": obj.url_or_path,
            "credentials_ref": "[configured]" if obj.credentials_ref else None,
            "run_schedule": obj.run_schedule,
            "enabled": obj.enabled,
            "priority_rank": obj.priority_rank,
            "notes": obj.notes,
            "scraping_config": obj.scraping_config or {},
            "created_at": obj.created_at,
            "updated_at": obj.updated_at,
        }
        return cls(**data)

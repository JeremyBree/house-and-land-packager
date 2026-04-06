"""PricingTemplate request/response schemas."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class TemplateRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    template_id: int
    brand: str
    file_path: str
    sheet_name: str
    data_start_row: int
    header_mappings: dict[str, Any]
    column_mappings: dict[str, Any]
    data_validations: dict[str, Any]
    created_at: datetime
    updated_at: datetime


class TemplateUpdateMappings(BaseModel):
    sheet_name: str | None = None
    data_start_row: int | None = None
    header_mappings: dict[str, Any] | None = None
    column_mappings: dict[str, Any] | None = None


class DataValidationsRead(BaseModel):
    """Wrapper for data validations extracted from a pricing template."""

    validations: dict[str, list[str]]

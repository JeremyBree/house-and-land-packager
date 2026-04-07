"""Pydantic schemas for the PDF ingestion workflow."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel


class PendingExtractionRead(BaseModel):
    extraction_id: int
    file_name: str
    file_path: str
    uploaded_by: int
    status: str
    extracted_data: dict[str, Any]
    extraction_notes: str | None = None
    reviewed_by: int | None = None
    reviewed_at: datetime | None = None
    review_notes: str | None = None
    ingestion_log_id: int | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ApproveInput(BaseModel):
    review_notes: str | None = None


class RejectInput(BaseModel):
    review_notes: str | None = None

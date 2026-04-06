"""IngestionLog response schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class IngestionLogRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    log_id: int
    agent_type: str
    source_identifier: str
    run_timestamp: datetime
    records_found: int
    records_created: int
    records_updated: int
    records_deactivated: int
    status: str
    error_detail: str | None = None

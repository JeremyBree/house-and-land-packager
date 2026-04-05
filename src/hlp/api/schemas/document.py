"""Estate document request/response schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DocumentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    document_id: int
    estate_id: int
    stage_id: int | None = None
    file_name: str
    file_type: str
    file_size: int
    description: str | None = None
    created_at: datetime
    download_url: str


class DocumentUploadResponse(DocumentRead):
    pass

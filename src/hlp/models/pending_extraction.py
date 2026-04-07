"""PendingExtraction model — stores AI-extracted data from PDF uploads pending review."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import Mapped, mapped_column

from hlp.database import Base
from hlp.models.mixins import TimestampMixin


class PendingExtraction(Base, TimestampMixin):
    __tablename__ = "pending_extractions"

    extraction_id: Mapped[int] = mapped_column(primary_key=True)
    file_name: Mapped[str] = mapped_column(String(500), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    uploaded_by: Mapped[int] = mapped_column(
        ForeignKey("profiles.profile_id"), nullable=False
    )
    status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False)
    extracted_data: Mapped[dict] = mapped_column(JSON, nullable=False)
    extraction_notes: Mapped[str | None] = mapped_column(Text)
    reviewed_by: Mapped[int | None] = mapped_column(
        ForeignKey("profiles.profile_id"), nullable=True
    )
    reviewed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    review_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    ingestion_log_id: Mapped[int | None] = mapped_column(
        ForeignKey("ingestion_logs.log_id"), nullable=True
    )

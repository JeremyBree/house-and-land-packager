"""PricingRequest model — sales submissions for pricing."""

from datetime import datetime
from typing import Any

from sqlalchemy import ARRAY, DateTime, ForeignKey, Index, JSON, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from hlp.database import Base
from hlp.models.enums import PricingRequestStatus, pg_pricing_request_status
from hlp.models.mixins import TimestampMixin


class PricingRequest(Base, TimestampMixin):
    __tablename__ = "pricing_requests"
    __table_args__ = (
        Index("idx_pricing_request_requester", "requester_id"),
        Index("idx_pricing_request_status", "status"),
    )

    request_id: Mapped[int] = mapped_column(primary_key=True)
    requester_id: Mapped[int] = mapped_column(ForeignKey("profiles.profile_id"), nullable=False)
    estate_id: Mapped[int] = mapped_column(ForeignKey("estates.estate_id"), nullable=False)
    stage_id: Mapped[int] = mapped_column(ForeignKey("estate_stages.stage_id"), nullable=False)
    brand: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[PricingRequestStatus] = mapped_column(
        pg_pricing_request_status,
        default=PricingRequestStatus.PENDING,
        nullable=False,
    )
    form_data: Mapped[dict[str, Any]] = mapped_column(
        JSONB().with_variant(JSON(), "sqlite"), default=dict, nullable=False
    )
    generated_file_path: Mapped[str | None] = mapped_column(String(500))
    completed_file_path: Mapped[str | None] = mapped_column(String(500))
    lot_numbers: Mapped[list[str]] = mapped_column(
        ARRAY(String(50)).with_variant(JSON(), "sqlite"), default=list, nullable=False
    )
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    price_breakdown: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB().with_variant(JSON(), "sqlite"), default=None
    )
    pricing_engine_version: Mapped[str | None] = mapped_column(String(20))

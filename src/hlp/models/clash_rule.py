"""ClashRule model — restricts lots from sharing design/facade combos."""

from datetime import datetime, timezone

from sqlalchemy import ARRAY, DateTime, ForeignKey, Index, JSON, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from hlp.database import Base


class ClashRule(Base):
    __tablename__ = "clash_rules"
    __table_args__ = (
        UniqueConstraint("estate_id", "stage_id", "lot_number", name="uq_clash_rule_scope"),
        Index("idx_clash_rule_estate_stage", "estate_id", "stage_id"),
    )

    rule_id: Mapped[int] = mapped_column(primary_key=True)
    estate_id: Mapped[int] = mapped_column(ForeignKey("estates.estate_id"), nullable=False)
    stage_id: Mapped[int] = mapped_column(ForeignKey("estate_stages.stage_id"), nullable=False)
    lot_number: Mapped[str] = mapped_column(String(50), nullable=False)
    cannot_match: Mapped[list[str]] = mapped_column(
        ARRAY(String(50)).with_variant(JSON(), "sqlite"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        nullable=False,
    )

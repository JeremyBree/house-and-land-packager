"""StatusHistory model — audit trail of lot status changes."""

from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from hlp.database import Base
from hlp.models.enums import LotStatus, pg_lot_status


class StatusHistory(Base):
    __tablename__ = "status_history"

    history_id: Mapped[int] = mapped_column(primary_key=True)
    lot_id: Mapped[int] = mapped_column(ForeignKey("stage_lots.lot_id"), nullable=False)
    previous_status: Mapped[LotStatus | None] = mapped_column(pg_lot_status)
    new_status: Mapped[LotStatus] = mapped_column(pg_lot_status, nullable=False)
    changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        nullable=False,
    )
    triggering_agent: Mapped[str] = mapped_column(String(50), nullable=False)
    source_detail: Mapped[str | None] = mapped_column(String(500))

    lot: Mapped["StageLot"] = relationship(back_populates="status_history")  # noqa: F821

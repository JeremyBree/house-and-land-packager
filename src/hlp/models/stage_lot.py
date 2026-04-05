"""StageLot model — individual land lot within an estate stage."""

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from hlp.database import Base
from hlp.models.enums import LotStatus, Source, pg_lot_status, pg_source
from hlp.models.mixins import TimestampMixin


class StageLot(Base, TimestampMixin):
    __tablename__ = "stage_lots"
    __table_args__ = (
        UniqueConstraint("stage_id", "lot_number", name="uq_stage_lot_number"),
        CheckConstraint("land_price IS NULL OR land_price >= 0", name="ck_lot_land_price_nonneg"),
        Index("idx_lot_stage_status", "stage_id", "status"),
        Index("idx_lot_price", "land_price"),
        Index("idx_lot_size", "size_sqm"),
        Index("idx_lot_frontage", "frontage"),
        Index("idx_lot_depth", "depth"),
        Index("idx_lot_title_date", "title_date"),
        Index("idx_lot_last_confirmed", "last_confirmed_date"),
    )

    lot_id: Mapped[int] = mapped_column(primary_key=True)
    stage_id: Mapped[int] = mapped_column(ForeignKey("estate_stages.stage_id"), nullable=False)
    lot_number: Mapped[str] = mapped_column(String(50), nullable=False)
    frontage: Mapped[Decimal | None] = mapped_column(Numeric(8, 2))
    depth: Mapped[Decimal | None] = mapped_column(Numeric(8, 2))
    size_sqm: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    corner_block: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    orientation: Mapped[str | None] = mapped_column(String(20))
    side_easement: Mapped[Decimal | None] = mapped_column(Numeric(6, 2))
    rear_easement: Mapped[Decimal | None] = mapped_column(Numeric(6, 2))
    street_name: Mapped[str | None] = mapped_column(String(255))
    land_price: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    build_price: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    package_price: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    design: Mapped[str | None] = mapped_column(String(255))
    facade: Mapped[str | None] = mapped_column(String(255))
    brand: Mapped[str | None] = mapped_column(String(100))
    status: Mapped[LotStatus] = mapped_column(
        pg_lot_status, default=LotStatus.AVAILABLE, nullable=False, index=True
    )
    substation: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    title_date: Mapped[date | None] = mapped_column(Date)
    last_confirmed_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    source: Mapped[Source | None] = mapped_column(pg_source)
    source_detail: Mapped[str | None] = mapped_column(String(500))

    stage: Mapped["EstateStage"] = relationship(back_populates="lots")  # noqa: F821
    status_history: Mapped[list["StatusHistory"]] = relationship(  # noqa: F821
        back_populates="lot", cascade="all, delete-orphan"
    )

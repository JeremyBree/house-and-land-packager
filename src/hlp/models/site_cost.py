"""SiteCostTier + SiteCostItem models — 3-tier site cost matrix."""

from sqlalchemy import ForeignKey, Index, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from hlp.database import Base


class SiteCostTier(Base):
    __tablename__ = "site_cost_tiers"

    tier_id: Mapped[int] = mapped_column(primary_key=True)
    tier_name: Mapped[str] = mapped_column(String(50), nullable=False)
    fall_min_mm: Mapped[int] = mapped_column(Integer, nullable=False)
    fall_max_mm: Mapped[int] = mapped_column(Integer, nullable=False)


class SiteCostItem(Base):
    __tablename__ = "site_cost_items"
    __table_args__ = (
        Index("idx_site_cost_item_tier_id", "tier_id"),
    )

    item_id: Mapped[int] = mapped_column(primary_key=True)
    tier_id: Mapped[int | None] = mapped_column(
        ForeignKey("site_cost_tiers.tier_id")
    )
    item_name: Mapped[str] = mapped_column(String(255), nullable=False)
    condition_type: Mapped[str | None] = mapped_column(String(100))
    condition_description: Mapped[str | None] = mapped_column(Text)
    cost_single_lt190: Mapped[float | None] = mapped_column(Numeric(10, 2))
    cost_double_lt190: Mapped[float | None] = mapped_column(Numeric(10, 2))
    cost_single_191_249: Mapped[float | None] = mapped_column(Numeric(10, 2))
    cost_double_191_249: Mapped[float | None] = mapped_column(Numeric(10, 2))
    cost_single_250_300: Mapped[float | None] = mapped_column(Numeric(10, 2))
    cost_double_250_300: Mapped[float | None] = mapped_column(Numeric(10, 2))
    cost_single_300plus: Mapped[float | None] = mapped_column(Numeric(10, 2))
    cost_double_300plus: Mapped[float | None] = mapped_column(Numeric(10, 2))
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    tier: Mapped["SiteCostTier | None"] = relationship()

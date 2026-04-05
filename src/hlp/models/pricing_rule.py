"""Pricing rule models — global (brand-wide) and stage-scoped."""

from decimal import Decimal

from sqlalchemy import ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from hlp.database import Base
from hlp.models.mixins import TimestampMixin


class GlobalPricingRule(Base, TimestampMixin):
    __tablename__ = "global_pricing_rules"

    rule_id: Mapped[int] = mapped_column(primary_key=True)
    brand: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    item_name: Mapped[str] = mapped_column(String(255), nullable=False)
    cost: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    condition: Mapped[str | None] = mapped_column(String(100))
    condition_value: Mapped[str | None] = mapped_column(String(255))
    cell_row: Mapped[int] = mapped_column(Integer, nullable=False)
    cell_col: Mapped[int] = mapped_column(Integer, nullable=False)
    cost_cell_row: Mapped[int] = mapped_column(Integer, nullable=False)
    cost_cell_col: Mapped[int] = mapped_column(Integer, nullable=False)
    category_id: Mapped[int | None] = mapped_column(ForeignKey("pricing_rule_categories.category_id"))
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)


class StagePricingRule(Base, TimestampMixin):
    __tablename__ = "stage_pricing_rules"

    rule_id: Mapped[int] = mapped_column(primary_key=True)
    estate_id: Mapped[int] = mapped_column(ForeignKey("estates.estate_id"), nullable=False)
    stage_id: Mapped[int] = mapped_column(ForeignKey("estate_stages.stage_id"), nullable=False)
    brand: Mapped[str] = mapped_column(String(100), nullable=False)
    item_name: Mapped[str] = mapped_column(String(255), nullable=False)
    cost: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    condition: Mapped[str | None] = mapped_column(String(100))
    condition_value: Mapped[str | None] = mapped_column(String(255))
    cell_row: Mapped[int] = mapped_column(Integer, nullable=False)
    cell_col: Mapped[int] = mapped_column(Integer, nullable=False)
    cost_cell_row: Mapped[int] = mapped_column(Integer, nullable=False)
    cost_cell_col: Mapped[int] = mapped_column(Integer, nullable=False)
    category_id: Mapped[int | None] = mapped_column(ForeignKey("pricing_rule_categories.category_id"))
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

"""UpgradeCategory + UpgradeItem models — upgrade/addon catalog."""

from datetime import date

from sqlalchemy import Date, ForeignKey, Index, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from hlp.database import Base
from hlp.models.mixins import TimestampMixin


class UpgradeCategory(Base):
    __tablename__ = "upgrade_categories"

    category_id: Mapped[int] = mapped_column(primary_key=True)
    brand: Mapped[str] = mapped_column(String(100), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)


class UpgradeItem(Base, TimestampMixin):
    __tablename__ = "upgrade_items"
    __table_args__ = (
        Index("idx_upgrade_item_brand", "brand"),
        Index("idx_upgrade_item_category_id", "category_id"),
    )

    upgrade_id: Mapped[int] = mapped_column(primary_key=True)
    brand: Mapped[str] = mapped_column(String(100), nullable=False)
    category_id: Mapped[int | None] = mapped_column(
        ForeignKey("upgrade_categories.category_id")
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    date_added: Mapped[date | None] = mapped_column(Date)
    notes: Mapped[str | None] = mapped_column(Text)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    category: Mapped["UpgradeCategory | None"] = relationship()

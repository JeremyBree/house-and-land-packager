"""PricingRuleCategory model — logical grouping for pricing rules."""

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from hlp.database import Base


class PricingRuleCategory(Base):
    __tablename__ = "pricing_rule_categories"

    category_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    brand: Mapped[str] = mapped_column(String(100), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

"""PricingConfig model — configurable pricing engine constants per brand."""

from decimal import Decimal

from sqlalchemy import Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from hlp.database import Base
from hlp.models.mixins import TimestampMixin


class PricingConfig(Base, TimestampMixin):
    """Configurable pricing engine constants. One row per brand.
    Admin can update these via the API without code changes."""

    __tablename__ = "pricing_configs"

    config_id: Mapped[int] = mapped_column(primary_key=True)
    brand: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    # Landscaping
    landscaping_rate_per_sqm: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), default=39, nullable=False
    )

    # Commission
    base_commission: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), default=33000, nullable=False
    )
    pct_commission_divisor: Mapped[Decimal] = mapped_column(
        Numeric(6, 4), default=Decimal("0.934"), nullable=False
    )

    # KDRB
    kdrb_surcharge: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), default=25000, nullable=False
    )

    # Holding costs
    holding_cost_rate: Mapped[Decimal] = mapped_column(
        Numeric(5, 4), default=Decimal("0.10"), nullable=False
    )

    # Lot discounts
    small_lot_threshold_sqm: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), default=300, nullable=False
    )
    small_lot_discount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), default=5000, nullable=False
    )
    dwellings_discount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), default=3000, nullable=False
    )

    # Corner block
    corner_block_savings: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), default=4620, nullable=False
    )

    # Rounding
    build_price_rounding: Mapped[int] = mapped_column(
        Integer, default=100, nullable=False
    )
    package_price_rounding: Mapped[int] = mapped_column(
        Integer, default=100, nullable=False
    )

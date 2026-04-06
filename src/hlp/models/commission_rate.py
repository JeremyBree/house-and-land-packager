"""CommissionRate model — BDM commission matrix per wholesale group."""

from sqlalchemy import ForeignKey, Index, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from hlp.database import Base
from hlp.models.mixins import TimestampMixin


class CommissionRate(Base, TimestampMixin):
    __tablename__ = "commission_rates"
    __table_args__ = (
        UniqueConstraint(
            "bdm_profile_id", "group_id", name="uq_commission_rate_bdm_group"
        ),
        Index("idx_commission_rate_bdm", "bdm_profile_id"),
        Index("idx_commission_rate_group", "group_id"),
    )

    rate_id: Mapped[int] = mapped_column(primary_key=True)
    bdm_profile_id: Mapped[int] = mapped_column(
        ForeignKey("profiles.profile_id"), nullable=False
    )
    group_id: Mapped[int] = mapped_column(
        ForeignKey("wholesale_groups.group_id"), nullable=False
    )
    commission_fixed: Mapped[float | None] = mapped_column(Numeric(10, 2))
    commission_pct: Mapped[float | None] = mapped_column(Numeric(5, 4))
    brand: Mapped[str] = mapped_column(String(100), nullable=False)

    bdm: Mapped["Profile"] = relationship()  # noqa: F821
    wholesale_group: Mapped["WholesaleGroup"] = relationship()  # noqa: F821

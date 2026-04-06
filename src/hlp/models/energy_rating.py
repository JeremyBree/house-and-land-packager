"""EnergyRating model — compliance cost matrix: house x garage x orientation."""

from sqlalchemy import ForeignKey, Index, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from hlp.database import Base
from hlp.models.mixins import TimestampMixin


class EnergyRating(Base, TimestampMixin):
    __tablename__ = "energy_ratings"
    __table_args__ = (
        UniqueConstraint(
            "design_id", "garage_side", "orientation",
            name="uq_energy_rating_design_garage_orient",
        ),
        Index("idx_energy_rating_design_id", "design_id"),
    )

    rating_id: Mapped[int] = mapped_column(primary_key=True)
    design_id: Mapped[int] = mapped_column(
        ForeignKey("house_designs.design_id"), nullable=False
    )
    garage_side: Mapped[str] = mapped_column(String(10), nullable=False)
    orientation: Mapped[str] = mapped_column(String(5), nullable=False)
    star_rating: Mapped[float] = mapped_column(Numeric(3, 1), nullable=False)
    best_worst: Mapped[str] = mapped_column(String(1), nullable=False)
    compliance_cost: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)

    design: Mapped["HouseDesign"] = relationship(back_populates="energy_ratings")  # noqa: F821

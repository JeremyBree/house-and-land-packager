"""HouseDesign + HouseFacade models — house catalog with per-facade pricing."""

from datetime import date

from sqlalchemy import (
    Boolean,
    Date,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from hlp.database import Base
from hlp.models.mixins import TimestampMixin


class HouseDesign(Base, TimestampMixin):
    __tablename__ = "house_designs"
    __table_args__ = (
        UniqueConstraint("brand", "house_name", name="uq_house_design_brand_name"),
        Index("idx_house_design_brand", "brand"),
        Index("idx_house_design_storey", "storey"),
    )

    design_id: Mapped[int] = mapped_column(primary_key=True)
    brand: Mapped[str] = mapped_column(String(100), nullable=False)
    house_name: Mapped[str] = mapped_column(String(100), nullable=False)
    base_price: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    storey: Mapped[str] = mapped_column(String(10), nullable=False)
    frontage: Mapped[float] = mapped_column(Numeric(6, 2), nullable=False)
    depth: Mapped[float] = mapped_column(Numeric(6, 2), nullable=False)
    gf_sqm: Mapped[float] = mapped_column(Numeric(8, 2), nullable=False)
    total_sqm: Mapped[float] = mapped_column(Numeric(8, 2), nullable=False)
    lot_total_sqm: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    squares: Mapped[int] = mapped_column(Integer, nullable=False)
    details: Mapped[str | None] = mapped_column(Text)
    effective_date: Mapped[date | None] = mapped_column(Date)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    facades: Mapped[list["HouseFacade"]] = relationship(
        back_populates="design", cascade="all, delete-orphan"
    )
    energy_ratings: Mapped[list["EnergyRating"]] = relationship(  # noqa: F821
        back_populates="design", cascade="all, delete-orphan"
    )


class HouseFacade(Base, TimestampMixin):
    __tablename__ = "house_facades"
    __table_args__ = (
        UniqueConstraint("design_id", "facade_name", name="uq_house_facade_design_name"),
        Index("idx_house_facade_design_id", "design_id"),
    )

    facade_id: Mapped[int] = mapped_column(primary_key=True)
    design_id: Mapped[int] = mapped_column(
        ForeignKey("house_designs.design_id"), nullable=False
    )
    facade_name: Mapped[str] = mapped_column(String(100), nullable=False)
    facade_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    facade_details: Mapped[str | None] = mapped_column(Text)
    is_included: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    design: Mapped["HouseDesign"] = relationship(back_populates="facades")

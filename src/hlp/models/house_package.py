"""HousePackage model — assigned house design on a specific lot."""

from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from hlp.database import Base
from hlp.models.mixins import TimestampMixin


class HousePackage(Base, TimestampMixin):
    __tablename__ = "house_packages"
    __table_args__ = (
        Index("idx_package_estate_stage", "estate_id", "stage_id"),
        Index("idx_package_design_facade", "design", "facade"),
    )

    package_id: Mapped[int] = mapped_column(primary_key=True)
    estate_id: Mapped[int] = mapped_column(ForeignKey("estates.estate_id"), nullable=False)
    stage_id: Mapped[int] = mapped_column(ForeignKey("estate_stages.stage_id"), nullable=False)
    lot_number: Mapped[str] = mapped_column(String(50), nullable=False)
    design: Mapped[str] = mapped_column(String(255), nullable=False)
    facade: Mapped[str] = mapped_column(String(255), nullable=False)
    colour_scheme: Mapped[str | None] = mapped_column(String(255))
    brand: Mapped[str] = mapped_column(String(100), nullable=False)
    source: Mapped[str | None] = mapped_column(String(500))
    status: Mapped[str | None] = mapped_column(String(50))
    flyer_path: Mapped[str | None] = mapped_column(String(500))
    design_id: Mapped[int | None] = mapped_column(ForeignKey("house_designs.design_id"))
    facade_id: Mapped[int | None] = mapped_column(ForeignKey("house_facades.facade_id"))

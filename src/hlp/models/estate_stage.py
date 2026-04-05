"""EstateStage model — a release stage within an estate."""

from datetime import date

from sqlalchemy import Date, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from hlp.database import Base
from hlp.models.enums import StageStatus, pg_stage_status
from hlp.models.mixins import TimestampMixin


class EstateStage(Base, TimestampMixin):
    __tablename__ = "estate_stages"

    stage_id: Mapped[int] = mapped_column(primary_key=True)
    estate_id: Mapped[int] = mapped_column(ForeignKey("estates.estate_id"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    lot_count: Mapped[int | None] = mapped_column(Integer)
    status: Mapped[StageStatus] = mapped_column(
        pg_stage_status, default=StageStatus.ACTIVE, nullable=False
    )
    release_date: Mapped[date | None] = mapped_column(Date)

    estate: Mapped["Estate"] = relationship(back_populates="stages")  # noqa: F821
    lots: Mapped[list["StageLot"]] = relationship(  # noqa: F821
        back_populates="stage", cascade="all, delete-orphan"
    )

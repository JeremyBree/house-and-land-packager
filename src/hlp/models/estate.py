"""Estate model — a residential development."""

from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from hlp.database import Base
from hlp.models.mixins import TimestampMixin


class Estate(Base, TimestampMixin):
    __tablename__ = "estates"

    estate_id: Mapped[int] = mapped_column(primary_key=True)
    developer_id: Mapped[int] = mapped_column(ForeignKey("developers.developer_id"), nullable=False)
    region_id: Mapped[int | None] = mapped_column(ForeignKey("regions.region_id"))
    estate_name: Mapped[str] = mapped_column(String(255), nullable=False)
    suburb: Mapped[str | None] = mapped_column(String(255), index=True)
    state: Mapped[str | None] = mapped_column(String(10))
    postcode: Mapped[str | None] = mapped_column(String(10))
    contact_name: Mapped[str | None] = mapped_column(String(255))
    contact_mobile: Mapped[str | None] = mapped_column(String(50))
    contact_email: Mapped[str | None] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)

    developer: Mapped["Developer"] = relationship(back_populates="estates")  # noqa: F821
    region: Mapped["Region | None"] = relationship(back_populates="estates")  # noqa: F821
    stages: Mapped[list["EstateStage"]] = relationship(  # noqa: F821
        back_populates="estate", cascade="all, delete-orphan"
    )

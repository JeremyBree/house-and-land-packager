"""TravelSurcharge model — suburb-based travel costs."""

from sqlalchemy import Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from hlp.database import Base


class TravelSurcharge(Base):
    __tablename__ = "travel_surcharges"

    surcharge_id: Mapped[int] = mapped_column(primary_key=True)
    suburb_name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    postcode: Mapped[str | None] = mapped_column(String(10))
    surcharge_amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    region_name: Mapped[str | None] = mapped_column(String(50))

"""PostcodeSiteCost model — rock removal cost by postcode."""

from sqlalchemy import Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from hlp.database import Base


class PostcodeSiteCost(Base):
    __tablename__ = "postcode_site_costs"

    postcode: Mapped[str] = mapped_column(String(10), primary_key=True)
    rock_removal_cost: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)

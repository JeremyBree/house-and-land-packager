"""FbcEscalationBand model — future build cost escalation bands."""

from sqlalchemy import Integer, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from hlp.database import Base


class FbcEscalationBand(Base):
    __tablename__ = "fbc_escalation_bands"
    __table_args__ = (
        UniqueConstraint("brand", "day_start", name="uq_fbc_escalation_brand_day_start"),
    )

    band_id: Mapped[int] = mapped_column(primary_key=True)
    brand: Mapped[str] = mapped_column(String(100), nullable=False)
    day_start: Mapped[int] = mapped_column(Integer, nullable=False)
    day_end: Mapped[int] = mapped_column(Integer, nullable=False)
    multiplier: Mapped[float] = mapped_column(Numeric(6, 4), nullable=False)

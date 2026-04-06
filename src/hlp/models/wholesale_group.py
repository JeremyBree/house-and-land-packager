"""WholesaleGroup model — wholesale group entities for BDM commissions."""

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from hlp.database import Base
from hlp.models.mixins import TimestampMixin


class WholesaleGroup(Base, TimestampMixin):
    __tablename__ = "wholesale_groups"

    group_id: Mapped[int] = mapped_column(primary_key=True)
    group_name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    gst_registered: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

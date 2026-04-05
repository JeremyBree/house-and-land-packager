"""Developer model — the company building an estate."""

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from hlp.database import Base
from hlp.models.mixins import TimestampMixin


class Developer(Base, TimestampMixin):
    __tablename__ = "developers"

    developer_id: Mapped[int] = mapped_column(primary_key=True)
    developer_name: Mapped[str] = mapped_column(String(255), nullable=False)
    developer_website: Mapped[str | None] = mapped_column(String(500))
    contact_email: Mapped[str | None] = mapped_column(String(255))
    notes: Mapped[str | None] = mapped_column(Text)

    estates: Mapped[list["Estate"]] = relationship(back_populates="developer")  # noqa: F821

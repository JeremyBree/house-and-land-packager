"""Profile model — user profile data."""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from hlp.database import Base
from hlp.models.mixins import TimestampMixin


class Profile(Base, TimestampMixin):
    __tablename__ = "profiles"

    profile_id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    job_title: Mapped[str | None] = mapped_column(String(255))
    email_verified: Mapped[bool] = mapped_column(default=False, nullable=False)

    user_roles: Mapped[list["UserRole"]] = relationship(  # noqa: F821
        back_populates="profile", cascade="all, delete-orphan"
    )

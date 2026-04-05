"""UserRole model — role assignments for profiles."""

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from hlp.database import Base
from hlp.models.enums import UserRoleType, pg_user_role_type


class UserRole(Base):
    __tablename__ = "user_roles"
    __table_args__ = (UniqueConstraint("profile_id", "role", name="uq_user_role"),)

    user_role_id: Mapped[int] = mapped_column(primary_key=True)
    profile_id: Mapped[int] = mapped_column(ForeignKey("profiles.profile_id"), nullable=False)
    role: Mapped[UserRoleType] = mapped_column(pg_user_role_type, nullable=False)

    profile: Mapped["Profile"] = relationship(back_populates="user_roles")  # noqa: F821

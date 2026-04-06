"""PricingTemplate model — brand-specific Excel template with cell mappings."""

from typing import Any

from sqlalchemy import Integer, JSON, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from hlp.database import Base
from hlp.models.mixins import TimestampMixin


class PricingTemplate(Base, TimestampMixin):
    __tablename__ = "pricing_templates"

    template_id: Mapped[int] = mapped_column(primary_key=True)
    brand: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    sheet_name: Mapped[str] = mapped_column(String(100), nullable=False)
    data_start_row: Mapped[int] = mapped_column(Integer, nullable=False)
    header_mappings: Mapped[dict[str, Any]] = mapped_column(
        JSONB().with_variant(JSON(), "sqlite"), default=dict, nullable=False
    )
    column_mappings: Mapped[dict[str, Any]] = mapped_column(
        JSONB().with_variant(JSON(), "sqlite"), default=dict, nullable=False
    )
    data_validations: Mapped[dict[str, Any]] = mapped_column(
        JSONB().with_variant(JSON(), "sqlite"), default=dict, nullable=False
    )

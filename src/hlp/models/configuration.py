"""Configuration model — data source configurations for ingestion agents."""

from typing import Any

from sqlalchemy import Boolean, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from hlp.database import Base
from hlp.models.enums import ConfigType, pg_config_type
from hlp.models.mixins import TimestampMixin


class Configuration(Base, TimestampMixin):
    __tablename__ = "configurations"

    config_id: Mapped[int] = mapped_column(primary_key=True)
    config_type: Mapped[ConfigType] = mapped_column(pg_config_type, nullable=False)
    estate_id: Mapped[int | None] = mapped_column(ForeignKey("estates.estate_id"))
    label: Mapped[str] = mapped_column(String(255), nullable=False)
    url_or_path: Mapped[str] = mapped_column(String(500), nullable=False)
    credentials_ref: Mapped[str | None] = mapped_column(String(255))
    run_schedule: Mapped[str | None] = mapped_column(String(100))
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    priority_rank: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)
    scraping_config: Mapped[dict[str, Any]] = mapped_column(
        JSONB().with_variant(JSON(), "sqlite"), default=dict, nullable=False
    )

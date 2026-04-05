"""IngestionLog model — structured log of agent runs."""

from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from hlp.database import Base
from hlp.models.enums import AgentType, IngestionStatus, pg_agent_type, pg_ingestion_status


class IngestionLog(Base):
    __tablename__ = "ingestion_logs"

    log_id: Mapped[int] = mapped_column(primary_key=True)
    agent_type: Mapped[AgentType] = mapped_column(pg_agent_type, nullable=False)
    source_identifier: Mapped[str] = mapped_column(String(500), nullable=False)
    run_timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        nullable=False,
    )
    records_found: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    records_created: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    records_updated: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    records_deactivated: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    status: Mapped[IngestionStatus] = mapped_column(pg_ingestion_status, nullable=False)
    error_detail: Mapped[str | None] = mapped_column(Text)

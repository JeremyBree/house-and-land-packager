"""GuidelineType + EstateDesignGuideline models — per-estate cost types."""

from sqlalchemy import ForeignKey, Index, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from hlp.database import Base


class GuidelineType(Base):
    __tablename__ = "guideline_types"

    type_id: Mapped[int] = mapped_column(primary_key=True)
    short_name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)


class EstateDesignGuideline(Base):
    __tablename__ = "estate_design_guidelines"
    __table_args__ = (
        UniqueConstraint(
            "estate_id", "stage_id", "type_id",
            name="uq_estate_guideline_estate_stage_type",
        ),
        Index("idx_estate_guideline_estate_stage", "estate_id", "stage_id"),
    )

    guideline_id: Mapped[int] = mapped_column(primary_key=True)
    estate_id: Mapped[int] = mapped_column(
        ForeignKey("estates.estate_id"), nullable=False
    )
    stage_id: Mapped[int | None] = mapped_column(
        ForeignKey("estate_stages.stage_id")
    )
    type_id: Mapped[int] = mapped_column(
        ForeignKey("guideline_types.type_id"), nullable=False
    )
    cost: Mapped[float | None] = mapped_column(Numeric(10, 2))
    override_text: Mapped[str | None] = mapped_column(Text)

    guideline_type: Mapped["GuidelineType"] = relationship()

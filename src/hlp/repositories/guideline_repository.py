"""Estate design guideline data access."""

from sqlalchemy import or_, select
from sqlalchemy.orm import Session, joinedload

from hlp.models.guideline import EstateDesignGuideline


def list_by_estate(
    db: Session, estate_id: int, stage_id: int | None = None
) -> list[EstateDesignGuideline]:
    stmt = (
        select(EstateDesignGuideline)
        .options(joinedload(EstateDesignGuideline.guideline_type))
        .where(EstateDesignGuideline.estate_id == estate_id)
    )
    if stage_id is not None:
        stmt = stmt.where(
            or_(
                EstateDesignGuideline.stage_id == stage_id,
                EstateDesignGuideline.stage_id.is_(None),
            )
        )
    else:
        stmt = stmt.where(EstateDesignGuideline.stage_id.is_(None))
    return list(db.execute(stmt).unique().scalars().all())

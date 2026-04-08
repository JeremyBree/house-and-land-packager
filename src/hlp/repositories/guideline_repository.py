"""Guideline type & estate design guideline data access."""

from sqlalchemy import or_, select
from sqlalchemy.orm import Session, joinedload

from hlp.models.guideline import EstateDesignGuideline, GuidelineType
from hlp.shared.exceptions import NotFoundError

# ---- GuidelineType -----------------------------------------------------------

def list_guideline_types(db: Session) -> list[GuidelineType]:
    stmt = select(GuidelineType).order_by(GuidelineType.sort_order, GuidelineType.short_name)
    return list(db.execute(stmt).scalars().all())


def get_guideline_type(db: Session, type_id: int) -> GuidelineType | None:
    return db.get(GuidelineType, type_id)


def create_guideline_type(db: Session, **fields) -> GuidelineType:
    obj = GuidelineType(**fields)
    db.add(obj)
    db.flush()
    return obj


def update_guideline_type(db: Session, type_id: int, **fields) -> GuidelineType:
    obj = get_guideline_type(db, type_id)
    if obj is None:
        raise NotFoundError(f"GuidelineType {type_id} not found")
    for k, v in fields.items():
        if v is not None:
            setattr(obj, k, v)
    db.flush()
    return obj


def delete_guideline_type(db: Session, type_id: int) -> None:
    obj = get_guideline_type(db, type_id)
    if obj is None:
        raise NotFoundError(f"GuidelineType {type_id} not found")
    db.delete(obj)
    db.flush()


# ---- EstateDesignGuideline ---------------------------------------------------

def list_by_estate(
    db: Session, estate_id: int, stage_id: int | None = None
) -> list[EstateDesignGuideline]:
    """Legacy helper used by pricing engine — returns estate-level + optional stage overlay."""
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


def list_estate_guidelines(
    db: Session,
    estate_id: int,
    stage_id: int | None = None,
) -> list[EstateDesignGuideline]:
    stmt = (
        select(EstateDesignGuideline)
        .options(joinedload(EstateDesignGuideline.guideline_type))
        .where(EstateDesignGuideline.estate_id == estate_id)
        .order_by(EstateDesignGuideline.guideline_id)
    )
    if stage_id is not None:
        stmt = stmt.where(EstateDesignGuideline.stage_id == stage_id)
    return list(db.execute(stmt).unique().scalars().all())


def get_estate_guideline(db: Session, guideline_id: int) -> EstateDesignGuideline | None:
    return db.get(EstateDesignGuideline, guideline_id)


def create_estate_guideline(db: Session, **fields) -> EstateDesignGuideline:
    obj = EstateDesignGuideline(**fields)
    db.add(obj)
    db.flush()
    return obj


def update_estate_guideline(db: Session, guideline_id: int, **fields) -> EstateDesignGuideline:
    obj = get_estate_guideline(db, guideline_id)
    if obj is None:
        raise NotFoundError(f"EstateDesignGuideline {guideline_id} not found")
    for k, v in fields.items():
        if v is not None:
            setattr(obj, k, v)
    db.flush()
    return obj


def delete_estate_guideline(db: Session, guideline_id: int) -> None:
    obj = get_estate_guideline(db, guideline_id)
    if obj is None:
        raise NotFoundError(f"EstateDesignGuideline {guideline_id} not found")
    db.delete(obj)
    db.flush()


def copy_guidelines(
    db: Session, source_estate_id: int, source_stage_id: int | None,
    target_estate_id: int, target_stage_id: int | None,
) -> int:
    """Copy guidelines from one estate/stage to another. Returns count copied."""
    sources = list_estate_guidelines(db, source_estate_id, source_stage_id)
    # Build set of existing (type_id,) for target
    existing_targets = set()
    target_guidelines = list_estate_guidelines(db, target_estate_id, target_stage_id)
    for g in target_guidelines:
        existing_targets.add(g.type_id)

    copied = 0
    for g in sources:
        if g.type_id in existing_targets:
            continue
        new_g = EstateDesignGuideline(
            estate_id=target_estate_id,
            stage_id=target_stage_id,
            type_id=g.type_id,
            cost=g.cost,
            override_text=g.override_text,
        )
        db.add(new_g)
        copied += 1
    db.flush()
    return copied

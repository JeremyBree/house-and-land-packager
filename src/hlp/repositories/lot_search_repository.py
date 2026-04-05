"""Land Search Interface data access — cross-estate lot search with joins."""

from typing import Any

from sqlalchemy import asc, desc, func, or_, select
from sqlalchemy.orm import Session

from hlp.api.schemas.lot_search import ALLOWED_SORT_FIELDS, LotSearchFilters
from hlp.models.developer import Developer
from hlp.models.estate import Estate
from hlp.models.estate_stage import EstateStage
from hlp.models.region import Region
from hlp.models.stage_lot import StageLot

# Map public sort keys to SQLAlchemy column references.
_SORT_COLUMN_MAP = {
    "land_price": StageLot.land_price,
    "size_sqm": StageLot.size_sqm,
    "frontage": StageLot.frontage,
    "lot_number": StageLot.lot_number,
    "estate_name": Estate.estate_name,
    "last_confirmed_date": StageLot.last_confirmed_date,
}


def _apply_filters(stmt, filters: LotSearchFilters):
    if filters.estate_ids:
        stmt = stmt.where(Estate.estate_id.in_(filters.estate_ids))
    if filters.developer_ids:
        stmt = stmt.where(Developer.developer_id.in_(filters.developer_ids))
    if filters.region_ids:
        stmt = stmt.where(Estate.region_id.in_(filters.region_ids))
    if filters.suburbs:
        lowered = [s.lower() for s in filters.suburbs]
        stmt = stmt.where(func.lower(Estate.suburb).in_(lowered))
    if filters.statuses:
        stmt = stmt.where(StageLot.status.in_(filters.statuses))
    if filters.price_min is not None:
        stmt = stmt.where(StageLot.land_price >= filters.price_min)
    if filters.price_max is not None:
        stmt = stmt.where(StageLot.land_price <= filters.price_max)
    if filters.size_min is not None:
        stmt = stmt.where(StageLot.size_sqm >= filters.size_min)
    if filters.size_max is not None:
        stmt = stmt.where(StageLot.size_sqm <= filters.size_max)
    if filters.frontage_min is not None:
        stmt = stmt.where(StageLot.frontage >= filters.frontage_min)
    if filters.depth_min is not None:
        stmt = stmt.where(StageLot.depth >= filters.depth_min)
    if filters.corner_block is not None:
        stmt = stmt.where(StageLot.corner_block == filters.corner_block)
    if filters.title_date_from is not None:
        stmt = stmt.where(StageLot.title_date >= filters.title_date_from)
    if filters.title_date_to is not None:
        stmt = stmt.where(StageLot.title_date <= filters.title_date_to)
    if filters.exclude_null_price:
        stmt = stmt.where(StageLot.land_price.is_not(None))
    if filters.text_search:
        term = f"%{filters.text_search.lower()}%"
        stmt = stmt.where(
            or_(
                func.lower(StageLot.lot_number).like(term),
                func.lower(Estate.estate_name).like(term),
                func.lower(Estate.suburb).like(term),
                func.lower(Developer.developer_name).like(term),
            )
        )
    return stmt


def _base_joined_select():
    """SELECT that joins lot -> stage -> estate -> developer and outer-joins region."""
    return (
        select(
            StageLot,
            EstateStage.name.label("stage_name"),
            Estate.estate_id.label("estate_id"),
            Estate.estate_name.label("estate_name"),
            Estate.suburb.label("estate_suburb"),
            Estate.state.label("estate_state"),
            Developer.developer_id.label("developer_id"),
            Developer.developer_name.label("developer_name"),
            Region.region_id.label("region_id"),
            Region.name.label("region_name"),
        )
        .join(EstateStage, StageLot.stage_id == EstateStage.stage_id)
        .join(Estate, EstateStage.estate_id == Estate.estate_id)
        .join(Developer, Estate.developer_id == Developer.developer_id)
        .outerjoin(Region, Estate.region_id == Region.region_id)
    )


def count(db: Session, filters: LotSearchFilters) -> int:
    stmt = (
        select(func.count(StageLot.lot_id))
        .select_from(StageLot)
        .join(EstateStage, StageLot.stage_id == EstateStage.stage_id)
        .join(Estate, EstateStage.estate_id == Estate.estate_id)
        .join(Developer, Estate.developer_id == Developer.developer_id)
        .outerjoin(Region, Estate.region_id == Region.region_id)
    )
    stmt = _apply_filters(stmt, filters)
    return int(db.execute(stmt).scalar_one())


def search(
    db: Session,
    filters: LotSearchFilters,
    page: int = 1,
    size: int = 50,
    sort_by: str = "land_price",
    sort_desc: bool = False,
) -> tuple[list[Any], int]:
    sort_key = sort_by if sort_by in ALLOWED_SORT_FIELDS else "land_price"
    sort_col = _SORT_COLUMN_MAP[sort_key]
    direction = desc if sort_desc else asc

    stmt = _base_joined_select()
    stmt = _apply_filters(stmt, filters)
    # Stable secondary sort on lot_id so pagination is deterministic.
    stmt = stmt.order_by(
        direction(sort_col).nulls_last(), asc(StageLot.lot_id)
    )
    stmt = stmt.offset((page - 1) * size).limit(size)

    total = count(db, filters)
    rows = list(db.execute(stmt).all())
    return rows, total


def search_all(
    db: Session,
    filters: LotSearchFilters,
    limit: int,
    sort_by: str = "land_price",
    sort_desc: bool = False,
) -> list[Any]:
    """Fetch up to ``limit`` matching rows (for export). No pagination."""
    sort_key = sort_by if sort_by in ALLOWED_SORT_FIELDS else "land_price"
    sort_col = _SORT_COLUMN_MAP[sort_key]
    direction = desc if sort_desc else asc

    stmt = _base_joined_select()
    stmt = _apply_filters(stmt, filters)
    stmt = stmt.order_by(
        direction(sort_col).nulls_last(), asc(StageLot.lot_id)
    ).limit(limit)
    return list(db.execute(stmt).all())

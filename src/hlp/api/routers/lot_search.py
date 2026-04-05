"""Land Search Interface (LSI) router — cross-estate lot search + exports."""

from __future__ import annotations

import math
from datetime import UTC, datetime
from typing import Annotated, Any

from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy.orm import Session

from hlp.api.deps import get_current_user, get_db
from hlp.api.schemas.lot_search import (
    LotSearchFilters,
    LotSearchRequest,
    LotSearchResponse,
    LotSearchResult,
)
from hlp.repositories import lot_search_repository
from hlp.shared.exceptions import ExportTooLargeError
from hlp.shared.export_service import export_lots_csv, export_lots_xlsx

router = APIRouter(
    prefix="/api/lots",
    tags=["lot-search"],
    dependencies=[Depends(get_current_user)],
)

MAX_EXPORT_ROWS = 5000


def _row_to_result(row: Any) -> LotSearchResult:
    """Convert a joined search row (Row tuple) into a LotSearchResult."""
    lot = row[0]
    # SQLAlchemy Row exposes labeled columns as attributes.
    return LotSearchResult(
        lot_id=lot.lot_id,
        stage_id=lot.stage_id,
        lot_number=lot.lot_number,
        frontage=lot.frontage,
        depth=lot.depth,
        size_sqm=lot.size_sqm,
        corner_block=lot.corner_block,
        orientation=lot.orientation,
        side_easement=lot.side_easement,
        rear_easement=lot.rear_easement,
        street_name=lot.street_name,
        land_price=lot.land_price,
        build_price=lot.build_price,
        package_price=lot.package_price,
        status=lot.status,
        substation=lot.substation,
        title_date=lot.title_date,
        last_confirmed_date=lot.last_confirmed_date,
        source=lot.source,
        created_at=lot.created_at,
        updated_at=lot.updated_at,
        estate_name=row.estate_name,
        estate_suburb=row.estate_suburb,
        estate_state=row.estate_state,
        developer_name=row.developer_name,
        region_name=row.region_name,
        stage_name=row.stage_name,
    )


def _filter_summary(filters: LotSearchFilters) -> dict[str, Any]:
    """Echo non-null filter values back to the client for display."""
    data = filters.model_dump(exclude_none=True, mode="json")
    # Drop default-falsey bool so UI only shows meaningful filters.
    if data.get("exclude_null_price") is False:
        data.pop("exclude_null_price", None)
    return data


@router.post("/search", response_model=LotSearchResponse)
def search_lots(
    payload: LotSearchRequest,
    db: Annotated[Session, Depends(get_db)],
) -> LotSearchResponse:
    rows, total = lot_search_repository.search(
        db,
        filters=payload.filters,
        page=payload.page,
        size=payload.size,
        sort_by=payload.normalized_sort(),
        sort_desc=payload.sort_desc,
    )
    pages = math.ceil(total / payload.size) if payload.size else 0
    return LotSearchResponse(
        items=[_row_to_result(r) for r in rows],
        total=total,
        page=payload.page,
        size=payload.size,
        pages=pages,
        filter_summary=_filter_summary(payload.filters),
    )


def _collect_export_rows(
    db: Session, filters: LotSearchFilters
) -> list[LotSearchResult]:
    total = lot_search_repository.count(db, filters)
    if total > MAX_EXPORT_ROWS:
        raise ExportTooLargeError(
            f"Export matches {total} rows; maximum is {MAX_EXPORT_ROWS}. "
            "Narrow your filters and try again."
        )
    raw_rows = lot_search_repository.search_all(db, filters, limit=MAX_EXPORT_ROWS)
    return [_row_to_result(r) for r in raw_rows]


def _timestamp() -> str:
    return datetime.now(UTC).strftime("%Y%m%d_%H%M%S")


@router.post("/export/csv")
def export_lots_csv_route(
    filters: LotSearchFilters,
    db: Annotated[Session, Depends(get_db)],
) -> Response:
    rows = _collect_export_rows(db, filters)
    content = export_lots_csv(rows)
    filename = f"lots_export_{_timestamp()}.csv"
    return Response(
        content=content,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post("/export/xlsx")
def export_lots_xlsx_route(
    filters: LotSearchFilters,
    db: Annotated[Session, Depends(get_db)],
) -> Response:
    rows = _collect_export_rows(db, filters)
    content = export_lots_xlsx(rows)
    filename = f"lots_export_{_timestamp()}.xlsx"
    return Response(
        content=content,
        media_type=(
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        ),
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )

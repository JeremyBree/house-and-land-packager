"""Dashboard router — aggregated metrics endpoint."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from hlp.api.deps import get_current_user, get_db
from hlp.api.schemas.dashboard import DashboardRead, RecentRequest
from hlp.models.estate import Estate
from hlp.models.estate_stage import EstateStage
from hlp.models.house_package import HousePackage
from hlp.models.pricing_request import PricingRequest
from hlp.models.stage_lot import StageLot
from hlp.shared import conflict_service

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get(
    "",
    response_model=DashboardRead,
    dependencies=[Depends(get_current_user)],
)
def get_dashboard(
    db: Annotated[Session, Depends(get_db)],
) -> DashboardRead:
    # Total estates
    total_estates = db.execute(
        select(func.count()).select_from(Estate)
    ).scalar_one()

    # Total lots
    total_lots = db.execute(
        select(func.count()).select_from(StageLot)
    ).scalar_one()

    # Total packages
    total_packages = db.execute(
        select(func.count()).select_from(HousePackage)
    ).scalar_one()

    # Active conflicts
    summary = conflict_service.get_conflict_summary(db)
    active_conflicts = summary["total_conflicts"]

    # Pending requests
    pending_requests = db.execute(
        select(func.count())
        .select_from(PricingRequest)
        .where(PricingRequest.status == "Pending")
    ).scalar_one()

    # Lot status breakdown
    status_rows = db.execute(
        select(StageLot.status, func.count())
        .group_by(StageLot.status)
    ).all()
    lot_status_breakdown = {}
    for status_val, cnt in status_rows:
        key = status_val.value if hasattr(status_val, "value") else str(status_val)
        lot_status_breakdown[key] = cnt

    # Recent requests (last 5)
    recent_stmt = (
        select(PricingRequest)
        .order_by(PricingRequest.request_id.desc())
        .limit(5)
    )
    recent_reqs = list(db.execute(recent_stmt).scalars().all())
    recent_requests = []
    for req in recent_reqs:
        # Look up estate/stage names
        estate_name = None
        stage_name = None
        estate = db.get(Estate, req.estate_id)
        if estate:
            estate_name = estate.estate_name
        stage = db.get(EstateStage, req.stage_id)
        if stage:
            stage_name = stage.name

        lot_count = len(req.lot_numbers) if req.lot_numbers else 0
        recent_requests.append(
            RecentRequest(
                request_id=req.request_id,
                brand=req.brand,
                status=req.status.value if hasattr(req.status, "value") else str(req.status),
                estate_name=estate_name,
                stage_name=stage_name,
                lot_count=lot_count,
                created_at=req.created_at,
            )
        )

    return DashboardRead(
        total_estates=total_estates,
        total_lots=total_lots,
        total_packages=total_packages,
        active_conflicts=active_conflicts,
        pending_requests=pending_requests,
        lot_status_breakdown=lot_status_breakdown,
        recent_requests=recent_requests,
    )

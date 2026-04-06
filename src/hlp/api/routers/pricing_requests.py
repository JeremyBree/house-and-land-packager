"""Pricing request router."""

import math
from typing import Annotated

from fastapi import APIRouter, Depends, File, Query, UploadFile, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from hlp.api.deps import get_current_user, get_db, require_roles
from hlp.api.schemas.common import PaginatedResponse
from hlp.api.schemas.estimator import EstimatorAssignment, EstimatorSubmission
from hlp.api.schemas.pricing_request import (
    PricingRequestCreate,
    PricingRequestDetailRead,
    PricingRequestRead,
)
from hlp.models.enums import UserRoleType
from hlp.models.profile import Profile
from hlp.shared import pricing_request_service
from hlp.shared.exceptions import PricingRequestNotFoundError
from hlp.shared.storage_service import get_storage_service

router = APIRouter(prefix="/api/pricing-requests", tags=["pricing-requests"])

require_admin_or_pricing = require_roles(UserRoleType.ADMIN, UserRoleType.PRICING)


@router.post(
    "",
    response_model=PricingRequestRead,
    status_code=status.HTTP_201_CREATED,
)
def submit_pricing_request(
    payload: PricingRequestCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Profile, Depends(get_current_user)],
) -> PricingRequestRead:
    request = pricing_request_service.submit_pricing_request(
        db, current_user.profile_id, payload
    )
    db.commit()
    db.refresh(request)
    return PricingRequestRead.model_validate(request)


@router.get(
    "",
    response_model=PaginatedResponse[PricingRequestRead],
)
def list_pricing_requests(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Profile, Depends(get_current_user)],
    page: int = Query(1, ge=1),
    size: int = Query(25, ge=1, le=200),
    status_filter: str | None = Query(None, alias="status"),
    brand: str | None = None,
    estate_id: int | None = None,
) -> PaginatedResponse[PricingRequestRead]:
    filters = {
        "status": status_filter,
        "brand": brand,
        "estate_id": estate_id,
    }
    return pricing_request_service.list_requests(
        db, current_user, filters, page, size
    )


@router.get(
    "/{request_id}",
    response_model=PricingRequestDetailRead,
)
def get_pricing_request(
    request_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Profile, Depends(get_current_user)],
) -> PricingRequestDetailRead:
    return pricing_request_service.get_request_detail(db, request_id, current_user)


@router.get("/{request_id}/download")
def download_generated_sheet(
    request_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Profile, Depends(get_current_user)],
):
    from hlp.repositories import pricing_request_repository

    request = pricing_request_repository.get_or_raise(db, request_id)
    if not request.generated_file_path:
        raise PricingRequestNotFoundError("Generated sheet not available")
    storage = get_storage_service()
    content = storage.read_file(request.generated_file_path)
    filename = request.generated_file_path.split("/")[-1]
    return StreamingResponse(
        iter([content]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post(
    "/{request_id}/fulfil",
    response_model=PricingRequestRead,
)
async def fulfil_pricing_request(
    request_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Profile, Depends(require_admin_or_pricing)],
    file: UploadFile = File(...),
) -> PricingRequestRead:
    content = await file.read()
    request = pricing_request_service.fulfil_pricing_request(
        db, request_id, content, file.filename or "completed.xlsx"
    )
    db.commit()
    db.refresh(request)
    return PricingRequestRead.model_validate(request)


@router.get("/{request_id}/download-completed")
def download_completed_sheet(
    request_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Profile, Depends(get_current_user)],
):
    from hlp.repositories import pricing_request_repository

    request = pricing_request_repository.get_or_raise(db, request_id)
    if not request.completed_file_path:
        raise PricingRequestNotFoundError("Completed sheet not available")
    storage = get_storage_service()
    content = storage.read_file(request.completed_file_path)
    filename = request.completed_file_path.split("/")[-1]
    return StreamingResponse(
        iter([content]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post(
    "/{request_id}/assign-estimator",
    response_model=PricingRequestRead,
)
def assign_estimator(
    request_id: int,
    payload: EstimatorAssignment,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Profile, Depends(require_admin_or_pricing)],
) -> PricingRequestRead:
    request = pricing_request_service.assign_estimator(
        db, request_id, payload.estimator_id, current_user
    )
    db.commit()
    db.refresh(request)
    return PricingRequestRead.model_validate(request)


@router.post(
    "/{request_id}/submit-estimate",
    response_model=PricingRequestDetailRead,
)
def submit_estimate(
    request_id: int,
    payload: EstimatorSubmission,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Profile, Depends(get_current_user)],
) -> PricingRequestDetailRead:
    request = pricing_request_service.submit_estimate(
        db, request_id, payload, current_user
    )
    db.commit()
    db.refresh(request)
    return pricing_request_service.get_request_detail(db, request_id, current_user)


@router.get(
    "/{request_id}/price-breakdown",
    response_model=list[dict],
)
def get_price_breakdown(
    request_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Profile, Depends(get_current_user)],
) -> list[dict]:
    """Get the price breakdown for a priced request."""
    from hlp.models.enums import PricingRequestStatus
    from hlp.repositories import pricing_request_repository

    request = pricing_request_repository.get_or_raise(db, request_id)
    if request.status in (PricingRequestStatus.PENDING, PricingRequestStatus.ESTIMATING):
        raise PricingRequestNotFoundError("Price breakdown not available until estimation is complete")
    return request.price_breakdown or []


@router.post(
    "/{request_id}/resubmit",
    response_model=dict,
)
def resubmit_pricing_request(
    request_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Profile, Depends(get_current_user)],
) -> dict:
    form_data = pricing_request_service.resubmit_request(db, request_id, current_user)
    return form_data


@router.delete(
    "/{request_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_pricing_request(
    request_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Profile, Depends(get_current_user)],
) -> None:
    pricing_request_service.delete_request(db, request_id, current_user)
    db.commit()

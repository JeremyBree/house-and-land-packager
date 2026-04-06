"""PricingRequest data access."""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from hlp.models.pricing_request import PricingRequest
from hlp.shared.exceptions import PricingRequestNotFoundError


def create(db: Session, **fields) -> PricingRequest:
    req = PricingRequest(**fields)
    db.add(req)
    db.flush()
    return req


def get(db: Session, request_id: int) -> PricingRequest | None:
    return db.get(PricingRequest, request_id)


def get_or_raise(db: Session, request_id: int) -> PricingRequest:
    req = get(db, request_id)
    if req is None:
        raise PricingRequestNotFoundError(f"Pricing request {request_id} not found")
    return req


def list_paginated(
    db: Session,
    filters: dict,
    page: int,
    size: int,
    requester_id: int | None = None,
) -> tuple[list[PricingRequest], int]:
    """List pricing requests with optional filtering.

    When ``requester_id`` is provided, only requests belonging to that user
    are returned (sales/requester role filtering).
    """
    base = select(PricingRequest)
    if requester_id is not None:
        base = base.where(PricingRequest.requester_id == requester_id)
    if filters.get("status"):
        base = base.where(PricingRequest.status == filters["status"])
    if filters.get("brand"):
        base = base.where(PricingRequest.brand == filters["brand"])
    if filters.get("estate_id") is not None:
        base = base.where(PricingRequest.estate_id == filters["estate_id"])

    total = db.execute(select(func.count()).select_from(base.subquery())).scalar_one()
    stmt = (
        base.order_by(PricingRequest.request_id.desc())
        .offset((page - 1) * size)
        .limit(size)
    )
    items = list(db.execute(stmt).scalars().all())
    return items, int(total)


def update(db: Session, request: PricingRequest, **fields) -> PricingRequest:
    for key, value in fields.items():
        setattr(request, key, value)
    db.flush()
    return request


def delete(db: Session, request_id: int) -> None:
    req = get_or_raise(db, request_id)
    db.delete(req)
    db.flush()

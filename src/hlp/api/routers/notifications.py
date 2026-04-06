"""Notification router."""

import math
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from hlp.api.deps import get_current_user, get_db
from hlp.api.schemas.common import PaginatedResponse
from hlp.api.schemas.notification import NotificationRead
from hlp.models.profile import Profile
from hlp.shared import notification_service

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


@router.get(
    "",
    response_model=PaginatedResponse[NotificationRead],
)
def list_notifications(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Profile, Depends(get_current_user)],
    page: int = Query(1, ge=1),
    size: int = Query(25, ge=1, le=200),
) -> PaginatedResponse[NotificationRead]:
    items, total = notification_service.list_all(
        db, current_user.profile_id, page, size
    )
    pages = math.ceil(total / size) if size else 0
    return PaginatedResponse[NotificationRead](
        items=[NotificationRead.model_validate(n) for n in items],
        total=total,
        page=page,
        size=size,
        pages=pages,
    )


@router.get(
    "/unread-count",
    response_model=dict,
)
def get_unread_count(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Profile, Depends(get_current_user)],
) -> dict:
    count = notification_service.unread_count(db, current_user.profile_id)
    return {"count": count}


@router.post(
    "/{notification_id}/read",
    response_model=NotificationRead,
)
def mark_notification_read(
    notification_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Profile, Depends(get_current_user)],
) -> NotificationRead:
    notif = notification_service.mark_read(
        db, notification_id, current_user.profile_id
    )
    db.commit()
    db.refresh(notif)
    return NotificationRead.model_validate(notif)


@router.post(
    "/read-all",
    response_model=dict,
)
def mark_all_notifications_read(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Profile, Depends(get_current_user)],
) -> dict:
    count = notification_service.mark_all_read(db, current_user.profile_id)
    db.commit()
    return {"updated": count}

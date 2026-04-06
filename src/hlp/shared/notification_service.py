"""Notification service: create, list, read status management."""

from __future__ import annotations

from sqlalchemy.orm import Session

from hlp.models.notification import Notification
from hlp.repositories import notification_repository
from hlp.shared.exceptions import NotAuthorizedError, NotFoundError


def create_notification(
    db: Session,
    profile_id: int,
    pricing_request_id: int,
    title: str,
    message: str,
) -> Notification:
    return notification_repository.create(
        db,
        profile_id=profile_id,
        pricing_request_id=pricing_request_id,
        title=title,
        message=message,
    )


def list_unread(db: Session, profile_id: int) -> list[Notification]:
    return notification_repository.list_unread(db, profile_id)


def list_all(
    db: Session, profile_id: int, page: int = 1, size: int = 25
) -> tuple[list[Notification], int]:
    return notification_repository.list_by_profile(db, profile_id, page, size)


def mark_read(db: Session, notification_id: int, profile_id: int) -> Notification:
    notif = notification_repository.get(db, notification_id)
    if notif is None:
        raise NotFoundError(f"Notification {notification_id} not found")
    if notif.profile_id != profile_id:
        raise NotAuthorizedError("Cannot mark another user's notification")
    return notification_repository.update_read(db, notif, True)


def mark_all_read(db: Session, profile_id: int) -> int:
    return notification_repository.mark_all_read(db, profile_id)


def unread_count(db: Session, profile_id: int) -> int:
    return notification_repository.count_unread(db, profile_id)

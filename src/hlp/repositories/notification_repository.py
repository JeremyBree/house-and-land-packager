"""Notification data access."""

from __future__ import annotations

from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from hlp.models.notification import Notification


def create(db: Session, **fields) -> Notification:
    notif = Notification(**fields)
    db.add(notif)
    db.flush()
    return notif


def list_by_profile(
    db: Session, profile_id: int, page: int = 1, size: int = 25
) -> tuple[list[Notification], int]:
    base = select(Notification).where(Notification.profile_id == profile_id)
    total = db.execute(select(func.count()).select_from(base.subquery())).scalar_one()
    stmt = (
        base.order_by(Notification.created_at.desc())
        .offset((page - 1) * size)
        .limit(size)
    )
    items = list(db.execute(stmt).scalars().all())
    return items, int(total)


def list_unread(db: Session, profile_id: int) -> list[Notification]:
    stmt = (
        select(Notification)
        .where(Notification.profile_id == profile_id, Notification.read == False)  # noqa: E712
        .order_by(Notification.created_at.desc())
    )
    return list(db.execute(stmt).scalars().all())


def get(db: Session, notification_id: int) -> Notification | None:
    return db.get(Notification, notification_id)


def update_read(db: Session, notification: Notification, read: bool) -> Notification:
    notification.read = read
    db.flush()
    return notification


def count_unread(db: Session, profile_id: int) -> int:
    stmt = select(func.count()).where(
        Notification.profile_id == profile_id,
        Notification.read == False,  # noqa: E712
    )
    return db.execute(stmt).scalar_one()


def mark_all_read(db: Session, profile_id: int) -> int:
    stmt = (
        update(Notification)
        .where(
            Notification.profile_id == profile_id,
            Notification.read == False,  # noqa: E712
        )
        .values(read=True)
    )
    result = db.execute(stmt)
    db.flush()
    return result.rowcount

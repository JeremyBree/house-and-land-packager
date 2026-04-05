"""Developer data access."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from hlp.models.developer import Developer
from hlp.shared.exceptions import NotFoundError


def list_all(db: Session) -> list[Developer]:
    stmt = select(Developer).order_by(Developer.developer_name)
    return list(db.execute(stmt).scalars().all())


def get(db: Session, developer_id: int) -> Developer | None:
    return db.get(Developer, developer_id)


def create(db: Session, **fields) -> Developer:
    dev = Developer(**fields)
    db.add(dev)
    db.flush()
    return dev


def update(db: Session, developer_id: int, **fields) -> Developer:
    dev = get(db, developer_id)
    if dev is None:
        raise NotFoundError(f"Developer {developer_id} not found")
    for k, v in fields.items():
        if v is not None:
            setattr(dev, k, v)
    db.flush()
    return dev


def delete(db: Session, developer_id: int) -> None:
    dev = get(db, developer_id)
    if dev is None:
        raise NotFoundError(f"Developer {developer_id} not found")
    db.delete(dev)
    db.flush()

"""Upgrade categories & items router."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from hlp.api.deps import get_current_user, get_db, require_admin
from hlp.api.schemas.upgrade_schema import (
    UpgradeCategoryCreate,
    UpgradeCategoryRead,
    UpgradeCategoryUpdate,
    UpgradeItemCreate,
    UpgradeItemRead,
    UpgradeItemUpdate,
)
from hlp.repositories import upgrade_repository
from hlp.shared.exceptions import NotFoundError

router = APIRouter(prefix="/api/upgrades", tags=["upgrades"])


# ---- Categories --------------------------------------------------------------

@router.get(
    "/categories",
    response_model=list[UpgradeCategoryRead],
    dependencies=[Depends(get_current_user)],
)
def list_categories(
    db: Annotated[Session, Depends(get_db)],
    brand: str | None = Query(default=None),
) -> list[UpgradeCategoryRead]:
    rows = upgrade_repository.list_categories(db, brand=brand)
    return [UpgradeCategoryRead.model_validate(r) for r in rows]


@router.post(
    "/categories",
    response_model=UpgradeCategoryRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)],
)
def create_category(
    payload: UpgradeCategoryCreate,
    db: Annotated[Session, Depends(get_db)],
) -> UpgradeCategoryRead:
    cat = upgrade_repository.create_category(db, **payload.model_dump())
    db.commit()
    db.refresh(cat)
    return UpgradeCategoryRead.model_validate(cat)


@router.patch(
    "/categories/{category_id}",
    response_model=UpgradeCategoryRead,
    dependencies=[Depends(require_admin)],
)
def update_category(
    category_id: int,
    payload: UpgradeCategoryUpdate,
    db: Annotated[Session, Depends(get_db)],
) -> UpgradeCategoryRead:
    cat = upgrade_repository.update_category(db, category_id, **payload.model_dump(exclude_unset=True))
    db.commit()
    db.refresh(cat)
    return UpgradeCategoryRead.model_validate(cat)


@router.delete(
    "/categories/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_admin)],
)
def delete_category(
    category_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> None:
    existing = upgrade_repository.get_category(db, category_id)
    if existing is None:
        raise NotFoundError(f"UpgradeCategory {category_id} not found")
    upgrade_repository.delete_category(db, category_id)
    db.commit()


# ---- Items -------------------------------------------------------------------

def _item_to_read(item) -> UpgradeItemRead:
    d = {c.key: getattr(item, c.key) for c in item.__table__.columns}
    d["category_name"] = item.category.name if item.category else None
    return UpgradeItemRead.model_validate(d)


@router.get(
    "/items",
    response_model=list[UpgradeItemRead],
    dependencies=[Depends(get_current_user)],
)
def list_items(
    db: Annotated[Session, Depends(get_db)],
    brand: str | None = Query(default=None),
    category_id: int | None = Query(default=None),
) -> list[UpgradeItemRead]:
    rows = upgrade_repository.list_items(db, brand=brand, category_id=category_id)
    return [_item_to_read(r) for r in rows]


@router.post(
    "/items",
    response_model=UpgradeItemRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)],
)
def create_item(
    payload: UpgradeItemCreate,
    db: Annotated[Session, Depends(get_db)],
) -> UpgradeItemRead:
    item = upgrade_repository.create_item(db, **payload.model_dump())
    db.commit()
    db.refresh(item)
    return _item_to_read(item)


@router.patch(
    "/items/{upgrade_id}",
    response_model=UpgradeItemRead,
    dependencies=[Depends(require_admin)],
)
def update_item(
    upgrade_id: int,
    payload: UpgradeItemUpdate,
    db: Annotated[Session, Depends(get_db)],
) -> UpgradeItemRead:
    item = upgrade_repository.update_item(db, upgrade_id, **payload.model_dump(exclude_unset=True))
    db.commit()
    db.refresh(item)
    return _item_to_read(item)


@router.delete(
    "/items/{upgrade_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_admin)],
)
def delete_item(
    upgrade_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> None:
    existing = upgrade_repository.get_item(db, upgrade_id)
    if existing is None:
        raise NotFoundError(f"UpgradeItem {upgrade_id} not found")
    upgrade_repository.delete_item(db, upgrade_id)
    db.commit()

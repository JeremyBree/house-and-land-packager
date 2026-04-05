"""House package router."""

import math
from typing import Annotated

from fastapi import APIRouter, Depends, File, Query, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from hlp.api.deps import get_current_user, get_db, require_admin
from hlp.api.schemas.common import PaginatedResponse
from hlp.api.schemas.house_package import (
    PackageCreate,
    PackageDetailRead,
    PackageRead,
    PackageUpdate,
)
from hlp.models.estate import Estate
from hlp.models.estate_stage import EstateStage
from hlp.models.stage_lot import StageLot
from hlp.repositories import (
    estate_repository,
    house_package_repository,
    stage_repository,
)
from hlp.shared import package_service
from hlp.shared.exceptions import (
    NotFoundError,
    PackageNotFoundError,
    StageNotFoundError,
)

router = APIRouter(prefix="/api/packages", tags=["packages"])


@router.get(
    "",
    response_model=PaginatedResponse[PackageRead],
    dependencies=[Depends(get_current_user)],
)
def list_packages(
    db: Annotated[Session, Depends(get_db)],
    estate_id: int | None = None,
    stage_id: int | None = None,
    brand: str | None = None,
    design: str | None = None,
    facade: str | None = None,
    lot_number: str | None = None,
    page: int = Query(1, ge=1),
    size: int = Query(25, ge=1, le=200),
) -> PaginatedResponse[PackageRead]:
    filters = {
        "estate_id": estate_id,
        "stage_id": stage_id,
        "brand": brand,
        "design": design,
        "facade": facade,
        "lot_number": lot_number,
    }
    items, total = house_package_repository.list_filtered(db, filters, page, size)
    pages = math.ceil(total / size) if size else 0
    return PaginatedResponse[PackageRead](
        items=[PackageRead.model_validate(p) for p in items],
        total=total,
        page=page,
        size=size,
        pages=pages,
    )


@router.post(
    "",
    response_model=PackageRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)],
)
def create_package(
    payload: PackageCreate,
    db: Annotated[Session, Depends(get_db)],
) -> PackageRead:
    if estate_repository.get(db, payload.estate_id) is None:
        raise NotFoundError(f"Estate {payload.estate_id} not found")
    if stage_repository.get(db, payload.stage_id) is None:
        raise StageNotFoundError(f"Stage {payload.stage_id} not found")
    pkg = package_service.create_package(db, **payload.model_dump())
    db.commit()
    db.refresh(pkg)
    return PackageRead.model_validate(pkg)


@router.get(
    "/{package_id}",
    response_model=PackageDetailRead,
    dependencies=[Depends(get_current_user)],
)
def get_package(
    package_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> PackageDetailRead:
    pkg = house_package_repository.get(db, package_id)
    if pkg is None:
        raise PackageNotFoundError(f"Package {package_id} not found")
    estate = db.get(Estate, pkg.estate_id)
    stage = db.get(EstateStage, pkg.stage_id)
    lot_id = db.execute(
        select(StageLot.lot_id).where(
            StageLot.stage_id == pkg.stage_id,
            StageLot.lot_number == pkg.lot_number,
        )
    ).scalar_one_or_none()
    base = PackageRead.model_validate(pkg).model_dump()
    return PackageDetailRead(
        **base,
        estate_name=estate.estate_name if estate else None,
        stage_name=stage.name if stage else None,
        lot_id=lot_id,
    )


@router.patch(
    "/{package_id}",
    response_model=PackageRead,
    dependencies=[Depends(require_admin)],
)
def update_package(
    package_id: int,
    payload: PackageUpdate,
    db: Annotated[Session, Depends(get_db)],
) -> PackageRead:
    fields = payload.model_dump(exclude_unset=True)
    pkg = package_service.update_package(db, package_id, **fields)
    db.commit()
    db.refresh(pkg)
    return PackageRead.model_validate(pkg)


@router.delete(
    "/{package_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_admin)],
)
def delete_package(
    package_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> None:
    package_service.delete_package(db, package_id)
    db.commit()


@router.post(
    "/{package_id}/flyer",
    response_model=PackageRead,
    dependencies=[Depends(require_admin)],
)
async def upload_flyer(
    package_id: int,
    db: Annotated[Session, Depends(get_db)],
    file: UploadFile = File(...),
) -> PackageRead:
    content = await file.read()
    pkg = package_service.upload_flyer(
        db,
        package_id=package_id,
        file_name=file.filename or "flyer",
        content_type=file.content_type,
        content=content,
    )
    db.commit()
    db.refresh(pkg)
    return PackageRead.model_validate(pkg)


@router.delete(
    "/{package_id}/flyer",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_admin)],
)
def delete_flyer(
    package_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> None:
    package_service.delete_flyer(db, package_id)
    db.commit()

"""House package service: CRUD + lot field sync + flyer management."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from hlp.models.house_package import HousePackage
from hlp.models.stage_lot import StageLot
from hlp.repositories import house_package_repository
from hlp.shared.exceptions import (
    FileTooLargeError,
    PackageNotFoundError,
    UnsupportedFileTypeError,
)
from hlp.shared.storage_service import CATEGORY_PACKAGE_FLYERS, get_storage_service

MAX_FLYER_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB
_ALLOWED_FLYER_EXTS = {"pdf", "png", "jpg", "jpeg"}
_ALLOWED_FLYER_MIMES = {
    "application/pdf",
    "image/png",
    "image/jpeg",
    "image/jpg",
}


def _sync_lot_fields(
    db: Session,
    estate_id: int,
    stage_id: int,
    lot_number: str,
    design: str | None,
    facade: str | None,
    brand: str | None,
) -> None:
    """Update the StageLot row's design/facade/brand fields."""
    stmt = select(StageLot).where(
        StageLot.stage_id == stage_id, StageLot.lot_number == lot_number
    )
    lot = db.execute(stmt).scalar_one_or_none()
    if lot is None:
        return
    if design is not None:
        lot.design = design
    if facade is not None:
        lot.facade = facade
    if brand is not None:
        lot.brand = brand
    db.flush()


def _clear_lot_fields(
    db: Session, stage_id: int, lot_number: str
) -> None:
    stmt = select(StageLot).where(
        StageLot.stage_id == stage_id, StageLot.lot_number == lot_number
    )
    lot = db.execute(stmt).scalar_one_or_none()
    if lot is None:
        return
    lot.design = None
    lot.facade = None
    lot.brand = None
    db.flush()


def create_package(db: Session, **fields) -> HousePackage:
    pkg = house_package_repository.create(db, **fields)
    _sync_lot_fields(
        db,
        estate_id=pkg.estate_id,
        stage_id=pkg.stage_id,
        lot_number=pkg.lot_number,
        design=pkg.design,
        facade=pkg.facade,
        brand=pkg.brand,
    )
    return pkg


def update_package(db: Session, package_id: int, **fields) -> HousePackage:
    pkg = house_package_repository.update(db, package_id, **fields)
    _sync_lot_fields(
        db,
        estate_id=pkg.estate_id,
        stage_id=pkg.stage_id,
        lot_number=pkg.lot_number,
        design=pkg.design,
        facade=pkg.facade,
        brand=pkg.brand,
    )
    return pkg


def delete_package(db: Session, package_id: int) -> None:
    pkg = house_package_repository.get(db, package_id)
    if pkg is None:
        raise PackageNotFoundError(f"Package {package_id} not found")
    stage_id = pkg.stage_id
    lot_number = pkg.lot_number
    flyer_path = pkg.flyer_path
    house_package_repository.delete(db, package_id)
    # Only clear lot fields if no other packages remain on the lot
    remaining = house_package_repository.list_by_lot(
        db, pkg.estate_id, stage_id, lot_number
    )
    if not remaining:
        _clear_lot_fields(db, stage_id, lot_number)
    if flyer_path:
        try:
            get_storage_service().delete_file(flyer_path)
        except Exception:
            pass


def _validate_flyer(file_name: str, content_type: str | None, content: bytes) -> None:
    if len(content) > MAX_FLYER_SIZE_BYTES:
        raise FileTooLargeError(
            f"Flyer '{file_name}' exceeds the 10 MB limit ({len(content)} bytes)"
        )
    mime_ok = content_type and content_type.lower() in _ALLOWED_FLYER_MIMES
    ext_ok = False
    if "." in file_name:
        ext = file_name.rsplit(".", 1)[-1].lower()
        ext_ok = ext in _ALLOWED_FLYER_EXTS
    if not (mime_ok or ext_ok):
        raise UnsupportedFileTypeError(
            f"Flyer type not supported for '{file_name}' (content-type={content_type!r}). "
            "Allowed: PDF, PNG, JPG, JPEG"
        )


def upload_flyer(
    db: Session,
    package_id: int,
    file_name: str,
    content_type: str | None,
    content: bytes,
) -> HousePackage:
    pkg = house_package_repository.get(db, package_id)
    if pkg is None:
        raise PackageNotFoundError(f"Package {package_id} not found")
    _validate_flyer(file_name, content_type, content)
    storage = get_storage_service()
    # Delete old flyer if present
    if pkg.flyer_path:
        try:
            storage.delete_file(pkg.flyer_path)
        except Exception:
            pass
    stored_path, _ = storage.save_file(CATEGORY_PACKAGE_FLYERS, file_name, content)
    pkg.flyer_path = stored_path
    db.flush()
    return pkg


def delete_flyer(db: Session, package_id: int) -> None:
    pkg = house_package_repository.get(db, package_id)
    if pkg is None:
        raise PackageNotFoundError(f"Package {package_id} not found")
    if pkg.flyer_path:
        try:
            get_storage_service().delete_file(pkg.flyer_path)
        except Exception:
            pass
        pkg.flyer_path = None
        db.flush()

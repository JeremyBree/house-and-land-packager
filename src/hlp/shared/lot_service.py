"""Business logic for lot CRUD, status transitions, CSV upload, bulk create."""

from __future__ import annotations

import csv
import io
from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation

from sqlalchemy.orm import Session

from hlp.api.schemas.lot import LotCreate
from hlp.models.enums import LotStatus
from hlp.models.stage_lot import StageLot
from hlp.repositories import lot_repository, status_history_repository
from hlp.shared.exceptions import InvalidCsvError, LotNotFoundError

_BOOL_TRUE = {"yes", "true", "1", "y", "t"}
_BOOL_FALSE = {"no", "false", "0", "n", "f", ""}


def _parse_bool(value: str | None, field: str, row_num: int) -> bool:
    if value is None:
        return False
    v = value.strip().lower()
    if v in _BOOL_TRUE:
        return True
    if v in _BOOL_FALSE:
        return False
    raise InvalidCsvError(
        f"Row {row_num}: invalid boolean for '{field}': {value!r}"
    )


def _parse_decimal(value: str | None, field: str, row_num: int) -> Decimal | None:
    if value is None or value.strip() == "":
        return None
    try:
        return Decimal(value.strip())
    except (InvalidOperation, ValueError) as exc:
        raise InvalidCsvError(
            f"Row {row_num}: invalid decimal for '{field}': {value!r}"
        ) from exc


def _parse_date(value: str | None, field: str, row_num: int) -> date | None:
    if value is None or value.strip() == "":
        return None
    try:
        return datetime.strptime(value.strip(), "%Y-%m-%d").date()
    except ValueError as exc:
        raise InvalidCsvError(
            f"Row {row_num}: invalid date for '{field}' (expected YYYY-MM-DD): {value!r}"
        ) from exc


def _clean_str(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


def parse_csv_upload(content: bytes) -> list[LotCreate]:
    """Parse a CSV upload into a list of ``LotCreate`` rows.

    Row numbers in error messages are 1-indexed and include the header row
    (i.e. the first data row is row 2).
    """
    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise InvalidCsvError(f"File is not valid UTF-8: {exc}") from exc

    reader = csv.DictReader(io.StringIO(text))
    if reader.fieldnames is None:
        raise InvalidCsvError("CSV has no header row")

    # Normalise field names to lowercase stripped
    normalised_fields = {(name or "").strip().lower(): name for name in reader.fieldnames}
    if "lot_number" not in normalised_fields:
        raise InvalidCsvError("CSV is missing required column 'lot_number'")

    def col(row: dict, key: str) -> str | None:
        original = normalised_fields.get(key)
        if original is None:
            return None
        return row.get(original)

    results: list[LotCreate] = []
    for idx, row in enumerate(reader, start=2):  # header is row 1
        # Skip completely empty rows
        if not any((v or "").strip() for v in row.values()):
            continue
        lot_number = _clean_str(col(row, "lot_number"))
        if not lot_number:
            raise InvalidCsvError(f"Row {idx}: 'lot_number' is required")
        try:
            lot = LotCreate(
                lot_number=lot_number,
                frontage=_parse_decimal(col(row, "frontage"), "frontage", idx),
                depth=_parse_decimal(col(row, "depth"), "depth", idx),
                size_sqm=_parse_decimal(col(row, "size_sqm"), "size_sqm", idx),
                corner_block=_parse_bool(col(row, "corner_block"), "corner_block", idx),
                orientation=_clean_str(col(row, "orientation")),
                side_easement=_parse_decimal(col(row, "side_easement"), "side_easement", idx),
                rear_easement=_parse_decimal(col(row, "rear_easement"), "rear_easement", idx),
                street_name=_clean_str(col(row, "street_name")),
                land_price=_parse_decimal(col(row, "land_price"), "land_price", idx),
                build_price=_parse_decimal(col(row, "build_price"), "build_price", idx),
                package_price=_parse_decimal(col(row, "package_price"), "package_price", idx),
                title_date=_parse_date(col(row, "title_date"), "title_date", idx),
            )
        except InvalidCsvError:
            raise
        except Exception as exc:
            raise InvalidCsvError(f"Row {idx}: {exc}") from exc
        results.append(lot)
    return results


def bulk_create_lots(
    db: Session, stage_id: int, lots: list[LotCreate]
) -> tuple[int, int, list[dict]]:
    """Create lots in bulk. Skip ones whose (stage_id, lot_number) already exist.

    Returns ``(created, skipped, errors)``.
    """
    created = 0
    skipped = 0
    errors: list[dict] = []
    # Track duplicates within the same payload
    seen_numbers: set[str] = set()
    for idx, payload in enumerate(lots, start=1):
        lot_number = payload.lot_number
        if lot_number in seen_numbers:
            skipped += 1
            continue
        seen_numbers.add(lot_number)
        existing = lot_repository.get_by_stage_and_number(db, stage_id, lot_number)
        if existing is not None:
            skipped += 1
            continue
        try:
            fields = payload.model_dump()
            lot_repository.create(db, stage_id=stage_id, **fields)
            created += 1
        except Exception as exc:  # pragma: no cover - defensive
            errors.append({"row": idx, "error": str(exc)})
    return created, skipped, errors


def transition_lot_status(
    db: Session,
    lot_id: int,
    new_status: LotStatus,
    reason: str,
    triggering_user_email: str,
) -> StageLot:
    """Transition lot status and log to StatusHistory.

    Sprint 2: any transition is accepted, including refreshes where
    ``new_status == current_status``.
    """
    lot = lot_repository.get(db, lot_id)
    if lot is None:
        raise LotNotFoundError(f"Lot {lot_id} not found")
    previous_status = lot.status
    now = datetime.now(timezone.utc)  # noqa: UP017
    status_history_repository.create(
        db,
        lot_id=lot_id,
        previous_status=previous_status,
        new_status=new_status,
        changed_at=now,
        triggering_agent=f"manual:{triggering_user_email}",
        source_detail=reason,
    )
    lot.status = new_status
    lot.last_confirmed_date = now
    db.flush()
    return lot

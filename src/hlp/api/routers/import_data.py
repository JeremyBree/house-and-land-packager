"""Admin endpoint for importing pricing workbook data."""

import tempfile
from pathlib import Path

from fastapi import APIRouter, Depends, File, Query, UploadFile
from pydantic import BaseModel
from sqlalchemy.orm import Session

from hlp.api.deps import get_db, require_admin
from hlp.seeds.import_pricing_workbook import ImportResult, import_from_excel

router = APIRouter(prefix="/api/admin", tags=["admin"])


class ImportResultResponse(BaseModel):
    houses_created: int
    facades_created: int
    energy_ratings_created: int
    upgrades_created: int
    upgrade_categories_created: int
    wholesale_groups_created: int
    commission_rates_created: int
    travel_surcharges_created: int
    postcode_costs_created: int
    guideline_types_created: int
    estate_guidelines_created: int
    fbc_bands_created: int
    site_cost_tiers_created: int
    site_cost_items_created: int
    skipped: int
    errors: list[str]


def _result_to_response(result: ImportResult) -> ImportResultResponse:
    return ImportResultResponse(
        houses_created=result.houses_created,
        facades_created=result.facades_created,
        energy_ratings_created=result.energy_ratings_created,
        upgrades_created=result.upgrades_created,
        upgrade_categories_created=result.upgrade_categories_created,
        wholesale_groups_created=result.wholesale_groups_created,
        commission_rates_created=result.commission_rates_created,
        travel_surcharges_created=result.travel_surcharges_created,
        postcode_costs_created=result.postcode_costs_created,
        guideline_types_created=result.guideline_types_created,
        estate_guidelines_created=result.estate_guidelines_created,
        fbc_bands_created=result.fbc_bands_created,
        site_cost_tiers_created=result.site_cost_tiers_created,
        site_cost_items_created=result.site_cost_items_created,
        skipped=result.skipped,
        errors=result.errors,
    )


@router.post(
    "/import-pricing-workbook",
    response_model=ImportResultResponse,
    dependencies=[Depends(require_admin)],
    summary="Import pricing data from an Excel workbook",
)
def import_pricing_workbook(
    file: UploadFile = File(...),
    brand: str = Query(default="Hermitage Homes"),
    db: Session = Depends(get_db),
) -> ImportResultResponse:
    """Upload an .xlsm/.xlsx pricing workbook and import its data.

    All operations are idempotent (existing records are skipped).
    """
    # Validate file extension
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in (".xlsm", ".xlsx"):
        from fastapi import HTTPException

        raise HTTPException(status_code=400, detail="File must be .xlsm or .xlsx")

    # Save to temp file
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(file.file.read())
        tmp_path = tmp.name

    try:
        result = import_from_excel(db, tmp_path, brand)
        db.commit()
        return _result_to_response(result)
    except Exception:
        db.rollback()
        raise
    finally:
        Path(tmp_path).unlink(missing_ok=True)

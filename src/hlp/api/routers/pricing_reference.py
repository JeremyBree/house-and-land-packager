"""Pricing reference data router — travel surcharges, site costs, postcode costs, FBC bands."""

from typing import Annotated

from fastapi import APIRouter, Depends, File, Query, UploadFile, status
from sqlalchemy.orm import Session

from hlp.api.deps import get_current_user, get_db, require_admin
from hlp.api.schemas.pricing_reference_schema import (
    FbcEscalationBandCreate,
    FbcEscalationBandRead,
    FbcEscalationBandUpdate,
    PostcodeSiteCostCreate,
    PostcodeSiteCostRead,
    PostcodeSiteCostUpdate,
    SiteCostItemCreate,
    SiteCostItemRead,
    SiteCostItemUpdate,
    SiteCostTierCreate,
    SiteCostTierRead,
    SiteCostTierUpdate,
    TravelSurchargeCreate,
    TravelSurchargeRead,
    TravelSurchargeUpdate,
)
from hlp.api.schemas.common import CsvRowError, CsvUploadResult
from hlp.repositories import pricing_reference_repository as repo
from hlp.shared import csv_import_service

router = APIRouter(prefix="/api/pricing-reference", tags=["pricing-reference"])


# ── Travel Surcharges ──────────────────────────────────────────────


@router.get(
    "/travel-surcharges",
    response_model=list[TravelSurchargeRead],
    dependencies=[Depends(get_current_user)],
)
def list_travel_surcharges(
    db: Annotated[Session, Depends(get_db)],
) -> list[TravelSurchargeRead]:
    return [TravelSurchargeRead.model_validate(s) for s in repo.list_travel_surcharges(db)]


@router.post(
    "/travel-surcharges",
    response_model=TravelSurchargeRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)],
)
def create_travel_surcharge(
    db: Annotated[Session, Depends(get_db)],
    payload: TravelSurchargeCreate,
) -> TravelSurchargeRead:
    obj = repo.create_travel_surcharge(db, **payload.model_dump())
    db.commit()
    db.refresh(obj)
    return TravelSurchargeRead.model_validate(obj)


@router.patch(
    "/travel-surcharges/{surcharge_id}",
    response_model=TravelSurchargeRead,
    dependencies=[Depends(require_admin)],
)
def update_travel_surcharge(
    surcharge_id: int,
    payload: TravelSurchargeUpdate,
    db: Annotated[Session, Depends(get_db)],
) -> TravelSurchargeRead:
    obj = repo.update_travel_surcharge(db, surcharge_id, **payload.model_dump(exclude_unset=True))
    db.commit()
    db.refresh(obj)
    return TravelSurchargeRead.model_validate(obj)


@router.delete(
    "/travel-surcharges/{surcharge_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_admin)],
)
def delete_travel_surcharge(
    surcharge_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> None:
    repo.delete_travel_surcharge(db, surcharge_id)
    db.commit()


# ── Site Cost Tiers ────────────────────────────────────────────────


@router.get(
    "/site-cost-tiers",
    response_model=list[SiteCostTierRead],
    dependencies=[Depends(get_current_user)],
)
def list_site_cost_tiers(
    db: Annotated[Session, Depends(get_db)],
) -> list[SiteCostTierRead]:
    return [SiteCostTierRead.model_validate(t) for t in repo.list_site_cost_tiers(db)]


@router.post(
    "/site-cost-tiers",
    response_model=SiteCostTierRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)],
)
def create_site_cost_tier(
    db: Annotated[Session, Depends(get_db)],
    payload: SiteCostTierCreate,
) -> SiteCostTierRead:
    obj = repo.create_site_cost_tier(db, **payload.model_dump())
    db.commit()
    db.refresh(obj)
    return SiteCostTierRead.model_validate(obj)


@router.patch(
    "/site-cost-tiers/{tier_id}",
    response_model=SiteCostTierRead,
    dependencies=[Depends(require_admin)],
)
def update_site_cost_tier(
    tier_id: int,
    payload: SiteCostTierUpdate,
    db: Annotated[Session, Depends(get_db)],
) -> SiteCostTierRead:
    obj = repo.update_site_cost_tier(db, tier_id, **payload.model_dump(exclude_unset=True))
    db.commit()
    db.refresh(obj)
    return SiteCostTierRead.model_validate(obj)


@router.delete(
    "/site-cost-tiers/{tier_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_admin)],
)
def delete_site_cost_tier(
    tier_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> None:
    repo.delete_site_cost_tier(db, tier_id)
    db.commit()


# ── Site Cost Items ────────────────────────────────────────────────


@router.get(
    "/site-cost-items",
    response_model=list[SiteCostItemRead],
    dependencies=[Depends(get_current_user)],
)
def list_site_cost_items(
    db: Annotated[Session, Depends(get_db)],
    tier_id: int | None = Query(None),
) -> list[SiteCostItemRead]:
    return [SiteCostItemRead.model_validate(i) for i in repo.list_site_cost_items(db, tier_id=tier_id)]


@router.post(
    "/site-cost-items",
    response_model=SiteCostItemRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)],
)
def create_site_cost_item(
    db: Annotated[Session, Depends(get_db)],
    payload: SiteCostItemCreate,
) -> SiteCostItemRead:
    obj = repo.create_site_cost_item(db, **payload.model_dump())
    db.commit()
    db.refresh(obj)
    return SiteCostItemRead.model_validate(obj)


@router.patch(
    "/site-cost-items/{item_id}",
    response_model=SiteCostItemRead,
    dependencies=[Depends(require_admin)],
)
def update_site_cost_item(
    item_id: int,
    payload: SiteCostItemUpdate,
    db: Annotated[Session, Depends(get_db)],
) -> SiteCostItemRead:
    obj = repo.update_site_cost_item(db, item_id, **payload.model_dump(exclude_unset=True))
    db.commit()
    db.refresh(obj)
    return SiteCostItemRead.model_validate(obj)


@router.delete(
    "/site-cost-items/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_admin)],
)
def delete_site_cost_item(
    item_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> None:
    repo.delete_site_cost_item(db, item_id)
    db.commit()


# ── Postcode Site Costs ────────────────────────────────────────────


@router.get(
    "/postcode-costs",
    response_model=list[PostcodeSiteCostRead],
    dependencies=[Depends(get_current_user)],
)
def list_postcode_costs(
    db: Annotated[Session, Depends(get_db)],
) -> list[PostcodeSiteCostRead]:
    return [PostcodeSiteCostRead.model_validate(p) for p in repo.list_postcode_site_costs(db)]


@router.post(
    "/postcode-costs",
    response_model=PostcodeSiteCostRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)],
)
def create_postcode_cost(
    db: Annotated[Session, Depends(get_db)],
    payload: PostcodeSiteCostCreate,
) -> PostcodeSiteCostRead:
    obj = repo.create_postcode_site_cost(db, **payload.model_dump())
    db.commit()
    db.refresh(obj)
    return PostcodeSiteCostRead.model_validate(obj)


@router.patch(
    "/postcode-costs/{postcode}",
    response_model=PostcodeSiteCostRead,
    dependencies=[Depends(require_admin)],
)
def update_postcode_cost(
    postcode: str,
    payload: PostcodeSiteCostUpdate,
    db: Annotated[Session, Depends(get_db)],
) -> PostcodeSiteCostRead:
    obj = repo.update_postcode_site_cost(db, postcode, **payload.model_dump(exclude_unset=True))
    db.commit()
    db.refresh(obj)
    return PostcodeSiteCostRead.model_validate(obj)


@router.delete(
    "/postcode-costs/{postcode}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_admin)],
)
def delete_postcode_cost(
    postcode: str,
    db: Annotated[Session, Depends(get_db)],
) -> None:
    repo.delete_postcode_site_cost(db, postcode)
    db.commit()


# ── FBC Escalation Bands ──────────────────────────────────────────


@router.get(
    "/fbc-bands",
    response_model=list[FbcEscalationBandRead],
    dependencies=[Depends(get_current_user)],
)
def list_fbc_bands(
    db: Annotated[Session, Depends(get_db)],
    brand: str | None = Query(None),
) -> list[FbcEscalationBandRead]:
    return [FbcEscalationBandRead.model_validate(b) for b in repo.list_fbc_bands(db, brand=brand)]


@router.post(
    "/fbc-bands",
    response_model=FbcEscalationBandRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)],
)
def create_fbc_band(
    db: Annotated[Session, Depends(get_db)],
    payload: FbcEscalationBandCreate,
) -> FbcEscalationBandRead:
    obj = repo.create_fbc_band(db, **payload.model_dump())
    db.commit()
    db.refresh(obj)
    return FbcEscalationBandRead.model_validate(obj)


@router.patch(
    "/fbc-bands/{band_id}",
    response_model=FbcEscalationBandRead,
    dependencies=[Depends(require_admin)],
)
def update_fbc_band(
    band_id: int,
    payload: FbcEscalationBandUpdate,
    db: Annotated[Session, Depends(get_db)],
) -> FbcEscalationBandRead:
    obj = repo.update_fbc_band(db, band_id, **payload.model_dump(exclude_unset=True))
    db.commit()
    db.refresh(obj)
    return FbcEscalationBandRead.model_validate(obj)


@router.delete(
    "/fbc-bands/{band_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_admin)],
)
def delete_fbc_band(
    band_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> None:
    repo.delete_fbc_band(db, band_id)
    db.commit()


# ── CSV Uploads ───────────────────────────────────────────────────────


@router.post(
    "/travel-surcharges/upload-csv",
    response_model=CsvUploadResult,
    dependencies=[Depends(require_admin)],
)
async def upload_travel_surcharges_csv(
    db: Annotated[Session, Depends(get_db)],
    file: UploadFile = File(...),
) -> CsvUploadResult:
    content = await file.read()
    parsed = csv_import_service.parse_travel_surcharges_csv(content)
    created, skipped, errors = csv_import_service.bulk_create_travel_surcharges(db, parsed)
    db.commit()
    return CsvUploadResult(created=created, skipped=skipped, errors=[CsvRowError(**e) for e in errors])


@router.post(
    "/postcode-costs/upload-csv",
    response_model=CsvUploadResult,
    dependencies=[Depends(require_admin)],
)
async def upload_postcode_costs_csv(
    db: Annotated[Session, Depends(get_db)],
    file: UploadFile = File(...),
) -> CsvUploadResult:
    content = await file.read()
    parsed = csv_import_service.parse_postcode_costs_csv(content)
    created, skipped, errors = csv_import_service.bulk_create_postcode_costs(db, parsed)
    db.commit()
    return CsvUploadResult(created=created, skipped=skipped, errors=[CsvRowError(**e) for e in errors])


@router.post(
    "/fbc-bands/upload-csv",
    response_model=CsvUploadResult,
    dependencies=[Depends(require_admin)],
)
async def upload_fbc_bands_csv(
    db: Annotated[Session, Depends(get_db)],
    file: UploadFile = File(...),
) -> CsvUploadResult:
    content = await file.read()
    parsed = csv_import_service.parse_fbc_bands_csv(content)
    created, skipped, errors = csv_import_service.bulk_create_fbc_bands(db, parsed)
    db.commit()
    return CsvUploadResult(created=created, skipped=skipped, errors=[CsvRowError(**e) for e in errors])


@router.post(
    "/site-cost-tiers/upload-csv",
    response_model=CsvUploadResult,
    dependencies=[Depends(require_admin)],
)
async def upload_site_cost_tiers_csv(
    db: Annotated[Session, Depends(get_db)],
    file: UploadFile = File(...),
) -> CsvUploadResult:
    content = await file.read()
    parsed = csv_import_service.parse_site_cost_tiers_csv(content)
    created, skipped, errors = csv_import_service.bulk_create_site_cost_tiers(db, parsed)
    db.commit()
    return CsvUploadResult(created=created, skipped=skipped, errors=[CsvRowError(**e) for e in errors])


@router.post(
    "/site-cost-items/upload-csv",
    response_model=CsvUploadResult,
    dependencies=[Depends(require_admin)],
)
async def upload_site_cost_items_csv(
    db: Annotated[Session, Depends(get_db)],
    file: UploadFile = File(...),
) -> CsvUploadResult:
    content = await file.read()
    parsed = csv_import_service.parse_site_cost_items_csv(content)
    created, skipped, errors = csv_import_service.bulk_create_site_cost_items(db, parsed)
    db.commit()
    return CsvUploadResult(created=created, skipped=skipped, errors=[CsvRowError(**e) for e in errors])

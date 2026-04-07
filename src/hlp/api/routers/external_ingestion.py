"""External ingestion router — API-key-authenticated endpoints for agents to push data."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from hlp.api.deps import get_api_key_agent, get_db
from hlp.api.schemas.external_ingestion_schema import (
    EstateUpsertInput,
    EstateUpsertResponse,
    GuidelineUpsertInput,
    GuidelineUpsertResponse,
    LotBulkUpsertInput,
    LotBulkUpsertResponse,
    StageUpsertInput,
    StageUpsertResponse,
)
from hlp.models.api_key import ApiKey
from hlp.models.developer import Developer
from hlp.models.enums import Source
from hlp.models.estate import Estate
from hlp.models.estate_stage import EstateStage
from hlp.models.guideline import EstateDesignGuideline, GuidelineType
from hlp.models.region import Region
from hlp.models.stage_lot import StageLot
from hlp.shared.exceptions import NotFoundError

router = APIRouter(prefix="/api/external/ingestion", tags=["external-ingestion"])


@router.post("/estates", response_model=EstateUpsertResponse)
def upsert_estate(
    body: EstateUpsertInput,
    agent: Annotated[ApiKey, Depends(get_api_key_agent)],
    db: Annotated[Session, Depends(get_db)],
):
    """Upsert estate data. Find by name (case-insensitive), create or update."""
    # Find existing estate
    stmt = select(Estate).where(func.lower(Estate.estate_name) == body.estate_name.lower())
    estate = db.execute(stmt).scalar_one_or_none()

    if estate is not None:
        # Update existing
        if body.suburb is not None:
            estate.suburb = body.suburb
        if body.postcode is not None:
            estate.postcode = body.postcode
        if body.contact_name is not None:
            estate.contact_name = body.contact_name
        if body.contact_email is not None:
            estate.contact_email = body.contact_email
        if body.contact_mobile is not None:
            estate.contact_mobile = body.contact_mobile
        db.commit()
        return EstateUpsertResponse(
            estate_id=estate.estate_id,
            estate_name=estate.estate_name,
            action="updated",
        )

    # Find or create developer
    dev_stmt = select(Developer).where(
        func.lower(Developer.developer_name) == body.developer_name.lower()
    )
    developer = db.execute(dev_stmt).scalar_one_or_none()
    if developer is None:
        developer = Developer(developer_name=body.developer_name)
        db.add(developer)
        db.flush()

    # Find or create region
    region_id = None
    if body.region_name:
        region_stmt = select(Region).where(
            func.lower(Region.name) == body.region_name.lower()
        )
        region = db.execute(region_stmt).scalar_one_or_none()
        if region is None:
            region = Region(name=body.region_name)
            db.add(region)
            db.flush()
        region_id = region.region_id

    estate = Estate(
        estate_name=body.estate_name,
        developer_id=developer.developer_id,
        region_id=region_id,
        suburb=body.suburb,
        postcode=body.postcode,
        contact_name=body.contact_name,
        contact_email=body.contact_email,
        contact_mobile=body.contact_mobile,
    )
    db.add(estate)
    db.commit()
    return EstateUpsertResponse(
        estate_id=estate.estate_id,
        estate_name=estate.estate_name,
        action="created",
    )


@router.post("/estates/{estate_id}/stages", response_model=StageUpsertResponse)
def upsert_stage(
    estate_id: int,
    body: StageUpsertInput,
    agent: Annotated[ApiKey, Depends(get_api_key_agent)],
    db: Annotated[Session, Depends(get_db)],
):
    """Upsert a stage within an estate. Find by (estate_id, name), create or update."""
    # Verify estate exists
    estate = db.get(Estate, estate_id)
    if estate is None:
        raise NotFoundError(f"Estate {estate_id} not found")

    stmt = select(EstateStage).where(
        EstateStage.estate_id == estate_id,
        func.lower(EstateStage.name) == body.name.lower(),
    )
    stage = db.execute(stmt).scalar_one_or_none()

    if stage is not None:
        if body.lot_count is not None:
            stage.lot_count = body.lot_count
        if body.status is not None:
            stage.status = body.status
        if body.release_date is not None:
            stage.release_date = body.release_date
        db.commit()
        return StageUpsertResponse(stage_id=stage.stage_id, name=stage.name, action="updated")

    stage = EstateStage(
        estate_id=estate_id,
        name=body.name,
        lot_count=body.lot_count,
        release_date=body.release_date,
    )
    if body.status is not None:
        stage.status = body.status
    db.add(stage)
    db.commit()
    return StageUpsertResponse(stage_id=stage.stage_id, name=stage.name, action="created")


@router.post("/stages/{stage_id}/lots", response_model=LotBulkUpsertResponse)
def upsert_lots(
    stage_id: int,
    body: LotBulkUpsertInput,
    agent: Annotated[ApiKey, Depends(get_api_key_agent)],
    db: Annotated[Session, Depends(get_db)],
):
    """Bulk upsert lots for a stage. Find by (stage_id, lot_number), create or update."""
    # Verify stage exists
    stage = db.get(EstateStage, stage_id)
    if stage is None:
        raise NotFoundError(f"Stage {stage_id} not found")

    created = 0
    updated = 0

    for lot_input in body.lots:
        stmt = select(StageLot).where(
            StageLot.stage_id == stage_id,
            StageLot.lot_number == lot_input.lot_number,
        )
        lot = db.execute(stmt).scalar_one_or_none()

        if lot is not None:
            # Update existing lot
            if lot_input.street_name is not None:
                lot.street_name = lot_input.street_name
            if lot_input.frontage is not None:
                lot.frontage = lot_input.frontage
            if lot_input.depth is not None:
                lot.depth = lot_input.depth
            if lot_input.size_sqm is not None:
                lot.size_sqm = lot_input.size_sqm
            if lot_input.land_price is not None:
                lot.land_price = lot_input.land_price
            if lot_input.orientation is not None:
                lot.orientation = lot_input.orientation
            if lot_input.corner_block is not None:
                lot.corner_block = lot_input.corner_block
            lot.source = Source.MANUAL  # Mark as API-sourced
            updated += 1
        else:
            lot = StageLot(
                stage_id=stage_id,
                lot_number=lot_input.lot_number,
                street_name=lot_input.street_name,
                frontage=lot_input.frontage,
                depth=lot_input.depth,
                size_sqm=lot_input.size_sqm,
                land_price=lot_input.land_price,
                orientation=lot_input.orientation,
                corner_block=lot_input.corner_block or False,
                source=Source.MANUAL,
            )
            db.add(lot)
            created += 1

    db.commit()
    return LotBulkUpsertResponse(created=created, updated=updated, total=created + updated)


@router.post("/estates/{estate_id}/guidelines", response_model=GuidelineUpsertResponse)
def upsert_guidelines(
    estate_id: int,
    body: GuidelineUpsertInput,
    agent: Annotated[ApiKey, Depends(get_api_key_agent)],
    db: Annotated[Session, Depends(get_db)],
):
    """Upsert design guidelines for an estate."""
    # Verify estate exists
    estate = db.get(Estate, estate_id)
    if estate is None:
        raise NotFoundError(f"Estate {estate_id} not found")

    created = 0
    updated = 0

    for g in body.guidelines:
        # Find guideline type by short_name
        type_stmt = select(GuidelineType).where(
            func.lower(GuidelineType.short_name) == g.guideline_type.lower()
        )
        gtype = db.execute(type_stmt).scalar_one_or_none()
        if gtype is None:
            # Skip unknown guideline types
            continue

        # Find existing guideline
        gl_stmt = select(EstateDesignGuideline).where(
            EstateDesignGuideline.estate_id == estate_id,
            EstateDesignGuideline.type_id == gtype.type_id,
        )
        if body.stage_id is not None:
            gl_stmt = gl_stmt.where(EstateDesignGuideline.stage_id == body.stage_id)
        else:
            gl_stmt = gl_stmt.where(EstateDesignGuideline.stage_id.is_(None))

        guideline = db.execute(gl_stmt).scalar_one_or_none()

        if guideline is not None:
            if g.cost is not None:
                guideline.cost = g.cost
            if g.override_text is not None:
                guideline.override_text = g.override_text
            updated += 1
        else:
            guideline = EstateDesignGuideline(
                estate_id=estate_id,
                stage_id=body.stage_id,
                type_id=gtype.type_id,
                cost=g.cost,
                override_text=g.override_text,
            )
            db.add(guideline)
            created += 1

    db.commit()
    return GuidelineUpsertResponse(created=created, updated=updated)

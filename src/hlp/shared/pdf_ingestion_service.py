"""PDF ingestion service — upload, AI extraction, and approval workflow."""

from __future__ import annotations

import logging
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from hlp.agents.extraction.pdf_extractor import extract_from_pdf
from hlp.models.developer import Developer
from hlp.models.enums import AgentType, IngestionStatus, LotStatus
from hlp.models.estate import Estate
from hlp.models.estate_stage import EstateStage
from hlp.models.guideline import EstateDesignGuideline, GuidelineType
from hlp.models.ingestion_log import IngestionLog
from hlp.models.pending_extraction import PendingExtraction
from hlp.repositories import (
    estate_repository,
    lot_repository,
    pending_extraction_repository,
    stage_repository,
)
from hlp.shared.storage_service import CATEGORY_ESTATE_DOCUMENTS, get_storage_service

logger = logging.getLogger(__name__)


def upload_and_extract(
    db: Session,
    file_name: str,
    content_type: str,
    content: bytes,
    uploaded_by: int,
) -> PendingExtraction:
    """Save uploaded PDF, run AI extraction, and create a pending extraction record."""
    # 1. Store the file
    storage = get_storage_service()
    stored_path, _size = storage.save_file(CATEGORY_ESTATE_DOCUMENTS, file_name, content)
    logger.info("Saved PDF '%s' to '%s' (%d bytes)", file_name, stored_path, _size)

    # 2. Run AI extraction
    extracted_data = extract_from_pdf(content)
    confidence = extracted_data.get("confidence", "unknown")
    notes = extracted_data.get("notes", "")

    # 3. Create PendingExtraction record
    record = pending_extraction_repository.create(
        db,
        file_name=file_name,
        file_path=stored_path,
        uploaded_by=uploaded_by,
        status="pending",
        extracted_data=extracted_data,
        extraction_notes=f"Confidence: {confidence}. {notes}" if notes else f"Confidence: {confidence}",
    )
    db.commit()
    db.refresh(record)
    logger.info(
        "Created PendingExtraction %d for '%s' (confidence=%s)",
        record.extraction_id,
        file_name,
        confidence,
    )
    return record


def _find_or_create_developer(db: Session, developer_name: str) -> Developer:
    """Find existing developer by name (case-insensitive) or create new."""
    stmt = select(Developer).where(
        func.lower(Developer.developer_name) == developer_name.lower()
    )
    dev = db.execute(stmt).scalar_one_or_none()
    if dev is None:
        dev = Developer(developer_name=developer_name)
        db.add(dev)
        db.flush()
        logger.info("Created developer '%s' (id=%d)", developer_name, dev.developer_id)
    return dev


def _find_or_create_estate(
    db: Session, estate_name: str, developer_id: int, **extra_fields
) -> Estate:
    """Find existing estate by name + developer or create new."""
    stmt = select(Estate).where(
        func.lower(Estate.estate_name) == estate_name.lower(),
        Estate.developer_id == developer_id,
    )
    estate = db.execute(stmt).scalar_one_or_none()
    if estate is None:
        estate = estate_repository.create(
            db,
            estate_name=estate_name,
            developer_id=developer_id,
            **extra_fields,
        )
        logger.info("Created estate '%s' (id=%d)", estate_name, estate.estate_id)
    else:
        # Update fields if provided
        for k, v in extra_fields.items():
            if v is not None:
                setattr(estate, k, v)
        db.flush()
    return estate


def _find_or_create_stage(
    db: Session, estate_id: int, stage_name: str
) -> EstateStage:
    """Find existing stage by name within estate or create new."""
    stmt = select(EstateStage).where(
        EstateStage.estate_id == estate_id,
        func.lower(EstateStage.name) == stage_name.lower(),
    )
    stage = db.execute(stmt).scalar_one_or_none()
    if stage is None:
        stage = stage_repository.create(db, estate_id=estate_id, name=stage_name)
        logger.info("Created stage '%s' for estate %d (id=%d)", stage_name, estate_id, stage.stage_id)
    return stage


def _find_guideline_type(db: Session, type_name: str) -> GuidelineType | None:
    """Find guideline type by short_name (case-insensitive)."""
    stmt = select(GuidelineType).where(
        func.lower(GuidelineType.short_name) == type_name.lower()
    )
    return db.execute(stmt).scalar_one_or_none()


def approve_extraction(
    db: Session,
    extraction_id: int,
    reviewed_by: int,
    review_notes: str | None = None,
) -> PendingExtraction:
    """Apply extracted data to the database and mark as approved.

    Creates/updates estates, stages, lots, and guidelines from the
    extracted data. Also creates an IngestionLog entry.
    """
    record = pending_extraction_repository.get(db, extraction_id)
    if record is None:
        from hlp.shared.exceptions import NotFoundError
        raise NotFoundError(f"PendingExtraction {extraction_id} not found")

    if record.status != "pending":
        raise ValueError(f"Extraction {extraction_id} is already {record.status}")

    data = record.extracted_data
    estates_data = data.get("estates", [])

    records_found = 0
    records_created = 0
    records_updated = 0

    for estate_data in estates_data:
        developer_name = estate_data.get("developer_name", "Unknown Developer")
        developer = _find_or_create_developer(db, developer_name)

        estate_fields: dict = {}
        for field in ("suburb", "postcode", "contact_name", "contact_email", "contact_mobile"):
            if estate_data.get(field):
                estate_fields[field] = estate_data[field]

        estate = _find_or_create_estate(
            db,
            estate_name=estate_data.get("estate_name", "Unknown Estate"),
            developer_id=developer.developer_id,
            **estate_fields,
        )

        stage_name = estate_data.get("stage_name", "1")
        stage = _find_or_create_stage(db, estate.estate_id, stage_name)

        # Process lots
        lots_data = estate_data.get("lots", [])
        for lot_data in lots_data:
            records_found += 1
            lot_number = str(lot_data.get("lot_number", ""))
            if not lot_number:
                continue

            existing_lot = lot_repository.get_by_stage_and_number(
                db, stage.stage_id, lot_number
            )

            lot_fields = {
                "street_name": lot_data.get("street_name"),
                "orientation": lot_data.get("orientation"),
                "corner_block": lot_data.get("corner_block", False),
                "status": LotStatus.AVAILABLE,
                "source": "pdf",
                "last_confirmed_date": datetime.now(UTC),
            }
            # Only set numeric fields if they have values
            for num_field in ("frontage", "depth", "size_sqm", "land_price"):
                val = lot_data.get(num_field)
                if val is not None:
                    lot_fields[num_field] = val

            if existing_lot is None:
                lot_repository.create(db, stage_id=stage.stage_id, lot_number=lot_number, **lot_fields)
                records_created += 1
            else:
                lot_repository.update(db, existing_lot.lot_id, **lot_fields)
                records_updated += 1

        # Process guidelines
        guidelines_data = estate_data.get("guidelines", [])
        for gd in guidelines_data:
            guideline_type_name = gd.get("guideline_type", "")
            if not guideline_type_name:
                continue

            gtype = _find_guideline_type(db, guideline_type_name)
            if gtype is None:
                # Create the guideline type
                gtype = GuidelineType(short_name=guideline_type_name, description=guideline_type_name)
                db.add(gtype)
                db.flush()

            # Check if guideline already exists for this estate+stage+type
            stmt = select(EstateDesignGuideline).where(
                EstateDesignGuideline.estate_id == estate.estate_id,
                EstateDesignGuideline.stage_id == stage.stage_id,
                EstateDesignGuideline.type_id == gtype.type_id,
            )
            existing_gl = db.execute(stmt).scalar_one_or_none()

            cost = gd.get("cost")
            notes = gd.get("notes", "")

            if existing_gl is None:
                gl = EstateDesignGuideline(
                    estate_id=estate.estate_id,
                    stage_id=stage.stage_id,
                    type_id=gtype.type_id,
                    cost=cost,
                    override_text=notes if notes else None,
                )
                db.add(gl)
            else:
                if cost is not None:
                    existing_gl.cost = cost
                if notes:
                    existing_gl.override_text = notes
            db.flush()

    # Create IngestionLog
    log = IngestionLog(
        agent_type=AgentType.PDF,
        source_identifier=record.file_name,
        records_found=records_found,
        records_created=records_created,
        records_updated=records_updated,
        records_deactivated=0,
        status=IngestionStatus.SUCCESS,
    )
    db.add(log)
    db.flush()

    # Update extraction record
    record.status = "approved"
    record.reviewed_by = reviewed_by
    record.reviewed_at = datetime.now(UTC)
    record.review_notes = review_notes
    record.ingestion_log_id = log.log_id
    db.flush()

    db.commit()
    db.refresh(record)

    logger.info(
        "Approved extraction %d: %d found, %d created, %d updated",
        extraction_id,
        records_found,
        records_created,
        records_updated,
    )
    return record


def reject_extraction(
    db: Session,
    extraction_id: int,
    reviewed_by: int,
    review_notes: str | None = None,
) -> PendingExtraction:
    """Mark an extraction as rejected."""
    record = pending_extraction_repository.get(db, extraction_id)
    if record is None:
        from hlp.shared.exceptions import NotFoundError
        raise NotFoundError(f"PendingExtraction {extraction_id} not found")

    if record.status != "pending":
        raise ValueError(f"Extraction {extraction_id} is already {record.status}")

    record.status = "rejected"
    record.reviewed_by = reviewed_by
    record.reviewed_at = datetime.now(UTC)
    record.review_notes = review_notes
    db.flush()
    db.commit()
    db.refresh(record)

    logger.info("Rejected extraction %d", extraction_id)
    return record

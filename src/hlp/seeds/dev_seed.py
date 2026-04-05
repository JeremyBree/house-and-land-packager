"""Idempotent dev seed: regions, developers, estates, users, stages, lots."""

import logging
import random
from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from hlp.models.developer import Developer
from hlp.models.enums import LotStatus, Source, StageStatus, UserRoleType
from hlp.models.estate import Estate
from hlp.models.estate_document import EstateDocument
from hlp.models.estate_stage import EstateStage
from hlp.models.region import Region
from hlp.models.stage_lot import StageLot
from hlp.repositories import profile_repository
from hlp.shared import user_service

logger = logging.getLogger(__name__)

REGIONS = [
    "Inner Melbourne",
    "North Melbourne",
    "South Melbourne",
    "East Melbourne",
    "West Melbourne",
    "Outer Melbourne",
]

DEVELOPERS = [
    {
        "developer_name": "Stockland",
        "developer_website": "https://www.stockland.com.au",
        "contact_email": "communities@stockland.com.au",
    },
    {
        "developer_name": "Mirvac",
        "developer_website": "https://www.mirvac.com",
        "contact_email": "residential@mirvac.com",
    },
    {
        "developer_name": "Villawood",
        "developer_website": "https://www.villawoodproperties.com",
        "contact_email": "info@villawoodproperties.com",
    },
    {
        "developer_name": "Satterley",
        "developer_website": "https://www.satterley.com.au",
        "contact_email": "info@satterley.com.au",
    },
    {
        "developer_name": "Frasers Property",
        "developer_website": "https://www.frasersproperty.com.au",
        "contact_email": "residential@frasersproperty.com.au",
    },
]

# (estate_name, developer_name, region_name, suburb, postcode)
ESTATES = [
    ("Cloverton", "Stockland", "North Melbourne", "Kalkallo", "3064"),
    ("Highlands", "Stockland", "North Melbourne", "Craigieburn", "3064"),
    ("Olivine", "Mirvac", "North Melbourne", "Donnybrook", "3064"),
    ("Smiths Lane", "Mirvac", "South Melbourne", "Clyde North", "3978"),
    ("Rathdowne", "Villawood", "West Melbourne", "Wollert", "3750"),
    ("Mount Atkinson", "Villawood", "West Melbourne", "Truganina", "3029"),
    ("Upper Point Cook", "Satterley", "West Melbourne", "Point Cook", "3030"),
    ("Banksia", "Satterley", "Outer Melbourne", "Tarneit", "3029"),
    ("Berwick Waters", "Frasers Property", "South Melbourne", "Clyde", "3978"),
    ("Life Point Cook", "Frasers Property", "West Melbourne", "Point Cook", "3030"),
]

USERS = [
    {
        "email": "admin@hbg.test",
        "first_name": "System",
        "last_name": "Admin",
        "job_title": "System Admin",
        "roles": [UserRoleType.ADMIN, UserRoleType.PRICING],
    },
    {
        "email": "pricing@hbg.test",
        "first_name": "Pricing",
        "last_name": "Manager",
        "job_title": "Pricing Manager",
        "roles": [UserRoleType.PRICING],
    },
    {
        "email": "sales1@hbg.test",
        "first_name": "Sales",
        "last_name": "RepOne",
        "job_title": "Sales Rep One",
        "roles": [UserRoleType.SALES, UserRoleType.REQUESTER],
    },
    {
        "email": "sales2@hbg.test",
        "first_name": "Sales",
        "last_name": "RepTwo",
        "job_title": "Sales Rep Two",
        "roles": [UserRoleType.SALES, UserRoleType.REQUESTER],
    },
    {
        "email": "requester@hbg.test",
        "first_name": "General",
        "last_name": "Requester",
        "job_title": "General Requester",
        "roles": [UserRoleType.REQUESTER],
    },
]

DEFAULT_PASSWORD = "Test1234!"


def seed_dev(db: Session) -> None:
    """Seed baseline dev data. Idempotent — skips existing rows."""
    region_map: dict[str, Region] = {}
    for name in REGIONS:
        existing = db.execute(select(Region).where(Region.name == name)).scalar_one_or_none()
        if existing is None:
            region = Region(name=name)
            db.add(region)
            db.flush()
            logger.info("Seeded region: %s", name)
            region_map[name] = region
        else:
            region_map[name] = existing

    dev_map: dict[str, Developer] = {}
    for dev_fields in DEVELOPERS:
        existing = db.execute(
            select(Developer).where(Developer.developer_name == dev_fields["developer_name"])
        ).scalar_one_or_none()
        if existing is None:
            dev = Developer(**dev_fields)
            db.add(dev)
            db.flush()
            logger.info("Seeded developer: %s", dev_fields["developer_name"])
            dev_map[dev_fields["developer_name"]] = dev
        else:
            dev_map[dev_fields["developer_name"]] = existing

    for estate_name, dev_name, region_name, suburb, postcode in ESTATES:
        existing = db.execute(
            select(Estate).where(Estate.estate_name == estate_name)
        ).scalar_one_or_none()
        if existing is None:
            estate = Estate(
                developer_id=dev_map[dev_name].developer_id,
                region_id=region_map[region_name].region_id,
                estate_name=estate_name,
                suburb=suburb,
                state="VIC",
                postcode=postcode,
                active=True,
            )
            db.add(estate)
            db.flush()
            logger.info("Seeded estate: %s (%s, %s)", estate_name, suburb, dev_name)

    _seed_stages_and_lots(db)
    _seed_sample_document(db)

    for user_fields in USERS:
        existing = profile_repository.get_by_email(db, user_fields["email"])
        if existing is None:
            user_service.create_user_with_roles(
                db,
                email=user_fields["email"],
                password=DEFAULT_PASSWORD,
                first_name=user_fields["first_name"],
                last_name=user_fields["last_name"],
                job_title=user_fields["job_title"],
                roles=user_fields["roles"],
            )
            logger.info("Seeded user: %s", user_fields["email"])
        else:
            logger.info("User already exists, skipping: %s", user_fields["email"])


_STREET_NAMES = [
    "Wattle Grove", "Banksia Drive", "Ironbark Way", "Eucalyptus Crescent",
    "Melaleuca Court", "Grevillea Road", "Jarrah Street", "Bottlebrush Lane",
]

_ORIENTATIONS = ["N", "S", "E", "W", "NE", "NW", "SE", "SW"]

_STATUS_DISTRIBUTION = (
    [LotStatus.AVAILABLE] * 6
    + [LotStatus.SOLD] * 2
    + [LotStatus.HOLD]
    + [LotStatus.DEPOSIT_TAKEN]
    + [LotStatus.UNAVAILABLE]
)


def _seed_stages_and_lots(db: Session) -> None:
    """Create 2-3 stages per estate and 8-15 lots per stage (idempotent)."""
    rng = random.Random(42)  # deterministic seed
    estates = list(db.execute(select(Estate)).scalars().all())
    for estate in estates:
        existing_stages = db.execute(
            select(EstateStage).where(EstateStage.estate_id == estate.estate_id)
        ).scalars().all()
        existing_names = {s.name for s in existing_stages}
        target_stage_count = rng.randint(2, 3)
        for idx in range(1, target_stage_count + 1):
            stage_name = f"Stage {idx}"
            if stage_name in existing_names:
                continue
            stage = EstateStage(
                estate_id=estate.estate_id,
                name=stage_name,
                lot_count=None,
                status=StageStatus.ACTIVE if idx == 1 else StageStatus.UPCOMING,
                release_date=date.today() + timedelta(days=30 * idx),
            )
            db.add(stage)
            db.flush()
            _seed_lots_for_stage(db, stage, rng)
            logger.info(
                "Seeded stage: %s for estate %s", stage_name, estate.estate_name
            )


def _seed_lots_for_stage(db: Session, stage: EstateStage, rng: random.Random) -> None:
    lot_count = rng.randint(8, 15)
    for i in range(1, lot_count + 1):
        lot_number = str(i)
        existing = db.execute(
            select(StageLot).where(
                StageLot.stage_id == stage.stage_id,
                StageLot.lot_number == lot_number,
            )
        ).scalar_one_or_none()
        if existing is not None:
            continue
        frontage = Decimal(rng.choice(["10.0", "12.5", "14.0", "16.0", "18.0"]))
        depth = Decimal(rng.choice(["28.0", "30.0", "32.0", "35.0"]))
        size = frontage * depth
        land_price = Decimal(rng.randrange(280_000, 480_001, 5_000))
        build_price = Decimal(rng.randrange(250_000, 400_001, 5_000))
        lot = StageLot(
            stage_id=stage.stage_id,
            lot_number=lot_number,
            frontage=frontage,
            depth=depth,
            size_sqm=size,
            corner_block=(i == 1 or i == lot_count),
            orientation=rng.choice(_ORIENTATIONS),
            street_name=rng.choice(_STREET_NAMES),
            land_price=land_price,
            build_price=build_price,
            package_price=land_price + build_price,
            status=rng.choice(_STATUS_DISTRIBUTION),
            substation=(i == 1 and rng.random() < 0.1),
            title_date=date.today() + timedelta(days=rng.randrange(30, 365)),
            source=Source.MANUAL,
        )
        db.add(lot)
    db.flush()


def _seed_sample_document(db: Session) -> None:
    """Create a dummy estate document (skips if storage unavailable or already seeded)."""
    existing = db.execute(select(EstateDocument)).first()
    if existing is not None:
        return
    first_estate = db.execute(select(Estate).order_by(Estate.estate_id)).scalars().first()
    if first_estate is None:
        return
    try:
        from hlp.shared.storage_service import (
            CATEGORY_ESTATE_DOCUMENTS,
            get_storage_service,
        )

        storage = get_storage_service()
        stored_path, size_bytes = storage.save_file(
            CATEGORY_ESTATE_DOCUMENTS,
            "sample-masterplan.pdf",
            b"%PDF-1.4 seed document placeholder\n",
        )
    except Exception as exc:
        logger.info("Skipping sample document seed (storage unavailable): %s", exc)
        return
    doc = EstateDocument(
        estate_id=first_estate.estate_id,
        stage_id=None,
        file_name="sample-masterplan.pdf",
        file_type="PDF",
        file_size=size_bytes,
        file_path=stored_path,
        description="Sample masterplan (seed data)",
    )
    db.add(doc)
    db.flush()
    logger.info("Seeded sample estate document for estate %s", first_estate.estate_name)

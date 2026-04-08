"""Idempotent dev seed: regions, developers, estates, users, stages, lots."""

import logging
import random
from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from hlp.models.clash_rule import ClashRule
from hlp.models.developer import Developer
from hlp.models.enums import LotStatus, Source, StageStatus, UserRoleType
from hlp.models.estate import Estate
from hlp.models.estate_document import EstateDocument
from hlp.models.estate_stage import EstateStage
from hlp.models.house_package import HousePackage
from hlp.models.pricing_config import PricingConfig
from hlp.models.pricing_rule import GlobalPricingRule, StagePricingRule
from hlp.models.pricing_rule_category import PricingRuleCategory
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
    _seed_clash_rules(db)
    _seed_house_packages(db)
    _seed_pricing_categories_and_rules(db)
    _seed_pricing_configs(db)
    _seed_pricing_workbook(db)

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


def _seed_clash_rules(db: Session) -> None:
    """Seed 3-5 clash rules for Cloverton Stage 1 (idempotent)."""
    cloverton = db.execute(
        select(Estate).where(Estate.estate_name == "Cloverton")
    ).scalar_one_or_none()
    if cloverton is None:
        return
    stage1 = db.execute(
        select(EstateStage).where(
            EstateStage.estate_id == cloverton.estate_id,
            EstateStage.name == "Stage 1",
        )
    ).scalar_one_or_none()
    if stage1 is None:
        return

    # (lot_number, cannot_match)
    rule_specs = [
        ("1", ["2", "3"]),
        ("2", ["1", "3"]),
        ("3", ["1", "2"]),
        ("5", ["6"]),
        ("6", ["5"]),
    ]
    for lot_number, cannot_match in rule_specs:
        existing = db.execute(
            select(ClashRule).where(
                ClashRule.estate_id == cloverton.estate_id,
                ClashRule.stage_id == stage1.stage_id,
                ClashRule.lot_number == lot_number,
            )
        ).scalar_one_or_none()
        if existing is not None:
            continue
        db.add(
            ClashRule(
                estate_id=cloverton.estate_id,
                stage_id=stage1.stage_id,
                lot_number=lot_number,
                cannot_match=cannot_match,
            )
        )
        logger.info(
            "Seeded clash rule: Cloverton Stage 1 lot %s cannot match %s",
            lot_number,
            cannot_match,
        )
    db.flush()


def _seed_house_packages(db: Session) -> None:
    """Seed 10-15 house packages with an intentional conflict (idempotent)."""
    existing_count = db.execute(select(HousePackage)).first()
    if existing_count is not None:
        return

    cloverton = db.execute(
        select(Estate).where(Estate.estate_name == "Cloverton")
    ).scalar_one_or_none()
    if cloverton is None:
        return
    cloverton_stage1 = db.execute(
        select(EstateStage).where(
            EstateStage.estate_id == cloverton.estate_id,
            EstateStage.name == "Stage 1",
        )
    ).scalar_one_or_none()
    if cloverton_stage1 is None:
        return

    # Get second estate (any active one) to spread packages around
    other_estates = db.execute(
        select(Estate).where(Estate.estate_id != cloverton.estate_id).limit(2)
    ).scalars().all()

    specs: list[dict] = []

    # Intentional conflict: Lots 1 and 2 on Cloverton Stage 1 same design+facade
    # (clash rule says 1 cannot match 2)
    specs.append(
        {
            "estate_id": cloverton.estate_id,
            "stage_id": cloverton_stage1.stage_id,
            "lot_number": "1",
            "design": "Aspen 28",
            "facade": "Hampton",
            "colour_scheme": "Coastal",
            "brand": "Hermitage Homes",
            "status": "Assigned",
        }
    )
    specs.append(
        {
            "estate_id": cloverton.estate_id,
            "stage_id": cloverton_stage1.stage_id,
            "lot_number": "2",
            "design": "Aspen 28",
            "facade": "Hampton",
            "colour_scheme": "Coastal",
            "brand": "Hermitage Homes",
            "status": "Assigned",
        }
    )
    # A non-conflicting package on Cloverton Stage 1
    specs.append(
        {
            "estate_id": cloverton.estate_id,
            "stage_id": cloverton_stage1.stage_id,
            "lot_number": "4",
            "design": "Ballarat 26",
            "facade": "Modern",
            "colour_scheme": "Stone",
            "brand": "Kingsbridge Homes",
            "status": "Assigned",
        }
    )
    # Lot 5/6 clash — design matches, facade differs, so NOT a conflict
    specs.append(
        {
            "estate_id": cloverton.estate_id,
            "stage_id": cloverton_stage1.stage_id,
            "lot_number": "5",
            "design": "Carlton 30",
            "facade": "Classic",
            "colour_scheme": "Sand",
            "brand": "Hermitage Homes",
            "status": "Assigned",
        }
    )
    specs.append(
        {
            "estate_id": cloverton.estate_id,
            "stage_id": cloverton_stage1.stage_id,
            "lot_number": "6",
            "design": "Carlton 30",
            "facade": "Contemporary",
            "colour_scheme": "Sand",
            "brand": "Hermitage Homes",
            "status": "Assigned",
        }
    )

    # Packages on other estates for variety
    designs = [
        ("Darwin 24", "Hampton", "Pearl", "Kingsbridge Homes"),
        ("Eaton 32", "Modern", "Charcoal", "Hermitage Homes"),
        ("Fairmont 26", "Heritage", "Cream", "Kingsbridge Homes"),
        ("Grampian 29", "Contemporary", "Stone", "Hermitage Homes"),
        ("Hawthorn 27", "Classic", "Coastal", "Kingsbridge Homes"),
        ("Indigo 25", "Modern", "Sand", "Hermitage Homes"),
        ("Jarrah 31", "Hampton", "Pearl", "Kingsbridge Homes"),
    ]
    lot_numbers = ["1", "2", "3", "4", "5", "6", "7"]
    idx = 0
    for estate in other_estates:
        estate_stages = db.execute(
            select(EstateStage)
            .where(EstateStage.estate_id == estate.estate_id)
            .limit(1)
        ).scalars().all()
        for stage in estate_stages:
            for _ in range(3):
                design, facade, colour, brand = designs[idx % len(designs)]
                lot_num = lot_numbers[idx % len(lot_numbers)]
                specs.append(
                    {
                        "estate_id": estate.estate_id,
                        "stage_id": stage.stage_id,
                        "lot_number": lot_num,
                        "design": design,
                        "facade": facade,
                        "colour_scheme": colour,
                        "brand": brand,
                        "status": "Assigned",
                    }
                )
                idx += 1

    for spec in specs:
        # Ensure the lot exists (otherwise skip)
        lot = db.execute(
            select(StageLot).where(
                StageLot.stage_id == spec["stage_id"],
                StageLot.lot_number == spec["lot_number"],
            )
        ).scalar_one_or_none()
        if lot is None:
            continue
        pkg = HousePackage(**spec)
        db.add(pkg)
        # Sync lot fields
        lot.design = spec["design"]
        lot.facade = spec["facade"]
        lot.brand = spec["brand"]
    db.flush()
    logger.info("Seeded %d house packages", len(specs))


def _seed_pricing_categories_and_rules(db: Session) -> None:
    """Seed pricing rule categories, global rules, and stage rules (idempotent)."""
    # --- Categories ---
    category_specs = [
        ("Commission", "Hermitage Homes", 0),
        ("Site Costs", "Hermitage Homes", 1),
        ("Commission", "Kingsbridge Homes", 0),
        ("Extras", "Kingsbridge Homes", 1),
    ]
    cat_map: dict[tuple[str, str], PricingRuleCategory] = {}
    for name, brand, sort_order in category_specs:
        existing = db.execute(
            select(PricingRuleCategory).where(
                PricingRuleCategory.name == name,
                PricingRuleCategory.brand == brand,
            )
        ).scalar_one_or_none()
        if existing is None:
            cat = PricingRuleCategory(name=name, brand=brand, sort_order=sort_order)
            db.add(cat)
            db.flush()
            logger.info("Seeded pricing category: %s (%s)", name, brand)
            cat_map[(name, brand)] = cat
        else:
            cat_map[(name, brand)] = existing

    # --- Global Rules ---
    hermitage_commission_id = cat_map[("Commission", "Hermitage Homes")].category_id
    hermitage_site_id = cat_map[("Site Costs", "Hermitage Homes")].category_id
    kingsbridge_commission_id = cat_map[("Commission", "Kingsbridge Homes")].category_id
    kingsbridge_extras_id = cat_map[("Extras", "Kingsbridge Homes")].category_id

    global_rule_specs = [
        # Hermitage rules
        {
            "brand": "Hermitage Homes",
            "item_name": "$35k Commission",
            "cost": Decimal("35000.00"),
            "condition": None,
            "condition_value": None,
            "cell_row": 10,
            "cell_col": 1,
            "cost_cell_row": 10,
            "cost_cell_col": 2,
            "category_id": hermitage_commission_id,
            "sort_order": 0,
        },
        {
            "brand": "Hermitage Homes",
            "item_name": "$35k Commission (Whittlesea)",
            "cost": Decimal("35000.00"),
            "condition": "wholesale_group:Whittlesea",
            "condition_value": "Whittlesea",
            "cell_row": 11,
            "cell_col": 1,
            "cost_cell_row": 11,
            "cost_cell_col": 2,
            "category_id": hermitage_commission_id,
            "sort_order": 1,
        },
        {
            "brand": "Hermitage Homes",
            "item_name": "$2,500 Corner Block",
            "cost": Decimal("2500.00"),
            "condition": "corner_block",
            "condition_value": None,
            "cell_row": 12,
            "cell_col": 1,
            "cost_cell_row": 12,
            "cost_cell_col": 2,
            "category_id": hermitage_site_id,
            "sort_order": 2,
        },
        {
            "brand": "Hermitage Homes",
            "item_name": "$1,500 Crossover",
            "cost": Decimal("1500.00"),
            "condition": "building_crossover",
            "condition_value": None,
            "cell_row": 13,
            "cell_col": 1,
            "cost_cell_row": 13,
            "cost_cell_col": 2,
            "category_id": hermitage_site_id,
            "sort_order": 3,
        },
        # Kingsbridge rules
        {
            "brand": "Kingsbridge Homes",
            "item_name": "$30k Commission",
            "cost": Decimal("30000.00"),
            "condition": None,
            "condition_value": None,
            "cell_row": 10,
            "cell_col": 1,
            "cost_cell_row": 10,
            "cost_cell_col": 2,
            "category_id": kingsbridge_commission_id,
            "sort_order": 0,
        },
        {
            "brand": "Kingsbridge Homes",
            "item_name": "$2,500 Corner Block",
            "cost": Decimal("2500.00"),
            "condition": "corner_block",
            "condition_value": None,
            "cell_row": 11,
            "cell_col": 1,
            "cost_cell_row": 11,
            "cost_cell_col": 2,
            "category_id": kingsbridge_extras_id,
            "sort_order": 1,
        },
        {
            "brand": "Kingsbridge Homes",
            "item_name": "$1,500 Crossover",
            "cost": Decimal("1500.00"),
            "condition": "building_crossover",
            "condition_value": None,
            "cell_row": 12,
            "cell_col": 1,
            "cost_cell_row": 12,
            "cost_cell_col": 2,
            "category_id": kingsbridge_extras_id,
            "sort_order": 2,
        },
    ]

    for spec in global_rule_specs:
        existing = db.execute(
            select(GlobalPricingRule).where(
                GlobalPricingRule.brand == spec["brand"],
                GlobalPricingRule.item_name == spec["item_name"],
            )
        ).scalar_one_or_none()
        if existing is None:
            db.add(GlobalPricingRule(**spec))
            logger.info(
                "Seeded global pricing rule: %s (%s)", spec["item_name"], spec["brand"]
            )
    db.flush()

    # --- Stage Rules (Cloverton Stage 1) ---
    cloverton = db.execute(
        select(Estate).where(Estate.estate_name == "Cloverton")
    ).scalar_one_or_none()
    if cloverton is None:
        return
    stage1 = db.execute(
        select(EstateStage).where(
            EstateStage.estate_id == cloverton.estate_id,
            EstateStage.name == "Stage 1",
        )
    ).scalar_one_or_none()
    if stage1 is None:
        return

    stage_rule_specs = [
        {
            "estate_id": cloverton.estate_id,
            "stage_id": stage1.stage_id,
            "brand": "Hermitage Homes",
            "item_name": "$500 Stage 1 Promo Discount",
            "cost": Decimal("-500.00"),
            "condition": None,
            "condition_value": None,
            "cell_row": 20,
            "cell_col": 1,
            "cost_cell_row": 20,
            "cost_cell_col": 2,
            "category_id": hermitage_commission_id,
            "sort_order": 0,
        },
        {
            "estate_id": cloverton.estate_id,
            "stage_id": stage1.stage_id,
            "brand": "Hermitage Homes",
            "item_name": "$3,000 KDRB Allowance",
            "cost": Decimal("3000.00"),
            "condition": "is_kdrb",
            "condition_value": None,
            "cell_row": 21,
            "cell_col": 1,
            "cost_cell_row": 21,
            "cost_cell_col": 2,
            "category_id": hermitage_site_id,
            "sort_order": 1,
        },
    ]

    for spec in stage_rule_specs:
        existing = db.execute(
            select(StagePricingRule).where(
                StagePricingRule.estate_id == spec["estate_id"],
                StagePricingRule.stage_id == spec["stage_id"],
                StagePricingRule.item_name == spec["item_name"],
            )
        ).scalar_one_or_none()
        if existing is None:
            db.add(StagePricingRule(**spec))
            logger.info(
                "Seeded stage pricing rule: %s (estate=%s, stage=%s)",
                spec["item_name"],
                spec["estate_id"],
                spec["stage_id"],
            )
    db.flush()


def _seed_pricing_configs(db: Session) -> None:
    """Seed default PricingConfig for both brands (idempotent)."""
    for brand in ("Hermitage Homes", "Kingsbridge Homes"):
        existing = db.execute(
            select(PricingConfig).where(PricingConfig.brand == brand)
        ).scalar_one_or_none()
        if existing is None:
            db.add(PricingConfig(brand=brand))
            logger.info("Seeded pricing config for %s (defaults)", brand)
    db.flush()


def _seed_pricing_workbook(db: Session) -> None:
    """One-time import of pricing reference data from the 2026 workbook.

    Only runs if no house designs exist yet (guard against re-importing).
    """
    import glob
    import os

    from hlp.models.house_design import HouseDesign

    existing_count = db.execute(
        select(HouseDesign.design_id).limit(1)
    ).scalar_one_or_none()
    if existing_count is not None:
        logger.info("Pricing data already seeded — skipping workbook import")
        return

    # Find the workbook in known locations
    workbook_patterns = [
        "/app/reference/*.xlsm",  # Docker container
        os.path.join(os.path.dirname(__file__), "..", "..", "..", "Reference", "Pricing sheet 2026.xlsm"),
    ]
    workbook_path = None
    for pattern in workbook_patterns:
        matches = glob.glob(pattern)
        if matches:
            workbook_path = matches[0]
            break

    if workbook_path is None:
        logger.warning("Pricing workbook not found — skipping reference data seed")
        return

    from hlp.seeds.import_pricing_workbook import import_from_excel

    logger.info("Seeding pricing reference data from: %s", workbook_path)
    result = import_from_excel(db, workbook_path, "Hermitage Homes")
    db.flush()
    logger.info(
        "Pricing seed complete: %d houses, %d facades, %d energy ratings, "
        "%d upgrades, %d commissions, %d surcharges, %d guidelines, %d skipped",
        result.houses_created, result.facades_created,
        result.energy_ratings_created, result.upgrades_created,
        result.commission_rates_created, result.travel_surcharges_created,
        result.estate_guidelines_created, result.skipped,
    )

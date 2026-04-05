"""Idempotent dev seed: regions, developers, estates, users."""

import logging

from sqlalchemy import select
from sqlalchemy.orm import Session

from hlp.models.developer import Developer
from hlp.models.enums import UserRoleType
from hlp.models.estate import Estate
from hlp.models.region import Region
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

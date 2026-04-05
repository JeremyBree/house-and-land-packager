"""Integration test fixtures: FastAPI TestClient bound to SQLite.

Sprint 1 ships 5 tables (profiles, user_roles, regions, developers, estates),
none of which use PostgreSQL-only column types. We therefore drive the full
FastAPI stack against an in-memory SQLite database for fast, Docker-free
integration tests. If/when later sprints add JSONB/ARRAY columns, swap this
fixture to testcontainers Postgres (see module docstring in parent conftest).
"""
from __future__ import annotations

from collections.abc import Iterator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from hlp.api.deps import get_db as api_get_db
from hlp.api.main import create_app
from hlp.database import get_db as db_get_db
from hlp.models.enums import UserRoleType
from hlp.shared import user_service

TEST_USERS = {
    "admin": {
        "email": "admin@it.example.com",
        "password": "Admin1234!",
        "first_name": "Admin",
        "last_name": "User",
        "job_title": "Admin",
        "roles": [UserRoleType.ADMIN],
    },
    "pricing": {
        "email": "pricing@it.example.com",
        "password": "Pricing1234!",
        "first_name": "Pricing",
        "last_name": "User",
        "job_title": "Pricing",
        "roles": [UserRoleType.PRICING],
    },
    "sales": {
        "email": "sales@it.example.com",
        "password": "Sales1234!",
        "first_name": "Sales",
        "last_name": "User",
        "job_title": "Sales",
        "roles": [UserRoleType.SALES],
    },
    "requester": {
        "email": "requester@it.example.com",
        "password": "Request1234!",
        "first_name": "Request",
        "last_name": "User",
        "job_title": "Requester",
        "roles": [UserRoleType.REQUESTER],
    },
}


@pytest.fixture(autouse=True)
def _truncate_tables(engine: Engine):
    """Wipe Sprint 1+2 tables before each integration test for isolation."""
    with engine.begin() as conn:
        for table in (
            "filter_presets",
            "user_roles",
            "profiles",
            "status_history",
            "stage_lots",
            "estate_documents",
            "estate_stages",
            "estates",
            "developers",
            "regions",
        ):
            conn.exec_driver_sql(f"DELETE FROM {table}")
    yield


@pytest.fixture()
def _session_factory(engine: Engine):
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)


@pytest.fixture()
def app(_session_factory) -> Iterator[FastAPI]:
    """FastAPI app with get_db overridden to use the test SQLite session."""
    # Create the app WITHOUT triggering lifespan (we skip the TestClient
    # context manager so startup/shutdown hooks don't run).
    application = create_app()

    def _override_get_db():
        session = _session_factory()
        try:
            yield session
        finally:
            session.close()

    # Both of these are used in different modules; override both.
    application.dependency_overrides[api_get_db] = _override_get_db
    application.dependency_overrides[db_get_db] = _override_get_db

    yield application
    application.dependency_overrides.clear()


@pytest.fixture()
def client(app: FastAPI) -> Iterator[TestClient]:
    # Do NOT use 'with TestClient(...)' — that runs the lifespan which tries
    # to create_all on Postgres-only tables. The app is fully functional
    # without lifespan because tables are already created by the engine fixture.
    # raise_server_exceptions=False lets us observe 500s from uncaught
    # SQLAlchemy IntegrityErrors (e.g. FK violations, unique violations) as
    # HTTP responses rather than raised exceptions.
    yield TestClient(app, raise_server_exceptions=False)


@pytest.fixture()
def seeded_users(_session_factory):
    """Create the four standard role users. Returns a dict keyed by role name."""
    session: Session = _session_factory()
    try:
        created = {}
        for key, data in TEST_USERS.items():
            profile = user_service.create_user_with_roles(
                session,
                email=data["email"],
                password=data["password"],
                first_name=data["first_name"],
                last_name=data["last_name"],
                job_title=data["job_title"],
                roles=data["roles"],
            )
            created[key] = {
                "profile_id": profile.profile_id,
                "email": profile.email,
                "password": data["password"],
            }
        session.commit()
        return created
    finally:
        session.close()


def _login(client: TestClient, email: str, password: str) -> str:
    r = client.post(
        "/api/auth/login",
        data={"username": email, "password": password},
    )
    assert r.status_code == 200, r.text
    return r.json()["access_token"]


@pytest.fixture()
def admin_token(client: TestClient, seeded_users) -> str:
    u = seeded_users["admin"]
    return _login(client, u["email"], u["password"])


@pytest.fixture()
def pricing_token(client: TestClient, seeded_users) -> str:
    u = seeded_users["pricing"]
    return _login(client, u["email"], u["password"])


@pytest.fixture()
def sales_token(client: TestClient, seeded_users) -> str:
    u = seeded_users["sales"]
    return _login(client, u["email"], u["password"])


@pytest.fixture()
def requester_token(client: TestClient, seeded_users) -> str:
    u = seeded_users["requester"]
    return _login(client, u["email"], u["password"])


def auth_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def admin_headers(admin_token: str) -> dict[str, str]:
    return auth_header(admin_token)


@pytest.fixture()
def sales_headers(sales_token: str) -> dict[str, str]:
    return auth_header(sales_token)


@pytest.fixture()
def pricing_headers(pricing_token: str) -> dict[str, str]:
    return auth_header(pricing_token)


@pytest.fixture()
def requester_headers(requester_token: str) -> dict[str, str]:
    return auth_header(requester_token)


# -----------------------------------------------------------------------------
# Sample data helpers (developers/regions/estates) for estate API tests.
# -----------------------------------------------------------------------------


@pytest.fixture()
def sample_data(_session_factory):
    """Seed a few regions, developers, and estates for list/filter tests."""
    from hlp.models.developer import Developer
    from hlp.models.estate import Estate
    from hlp.models.region import Region

    session: Session = _session_factory()
    try:
        regions = [Region(name=n) for n in ("North", "South", "East")]
        for r in regions:
            session.add(r)
        session.flush()

        devs = [
            Developer(developer_name="Stockland"),
            Developer(developer_name="Mirvac"),
        ]
        for d in devs:
            session.add(d)
        session.flush()

        estates = [
            Estate(
                developer_id=devs[0].developer_id,
                region_id=regions[0].region_id,
                estate_name="Cloverton",
                suburb="Kalkallo",
                postcode="3064",
                active=True,
            ),
            Estate(
                developer_id=devs[0].developer_id,
                region_id=regions[0].region_id,
                estate_name="Highlands",
                suburb="Craigieburn",
                postcode="3064",
                active=True,
            ),
            Estate(
                developer_id=devs[1].developer_id,
                region_id=regions[1].region_id,
                estate_name="Smiths Lane",
                suburb="Clyde North",
                postcode="3978",
                active=True,
            ),
            Estate(
                developer_id=devs[1].developer_id,
                region_id=regions[2].region_id,
                estate_name="Olivine",
                suburb="Donnybrook",
                postcode="3064",
                active=True,
            ),
            Estate(
                developer_id=devs[0].developer_id,
                region_id=regions[2].region_id,
                estate_name="Retired Estate",
                suburb="Gone",
                postcode="3000",
                active=False,
            ),
        ]
        for e in estates:
            session.add(e)
        session.commit()

        return {
            "regions": [
                {"region_id": r.region_id, "name": r.name} for r in regions
            ],
            "developers": [
                {"developer_id": d.developer_id, "developer_name": d.developer_name}
                for d in devs
            ],
            "estates": [
                {
                    "estate_id": e.estate_id,
                    "estate_name": e.estate_name,
                    "developer_id": e.developer_id,
                    "region_id": e.region_id,
                    "active": e.active,
                }
                for e in estates
            ],
        }
    finally:
        session.close()


# -----------------------------------------------------------------------------
# Sprint 2 fixtures: stages, lots, storage isolation, upload helpers.
# -----------------------------------------------------------------------------


@pytest.fixture()
def sample_stages_and_lots(_session_factory, sample_data):
    """Seed 2 stages under the first estate, each with 5 lots of varied statuses."""
    from hlp.models.enums import LotStatus, Source
    from hlp.models.estate_stage import EstateStage
    from hlp.models.stage_lot import StageLot

    session: Session = _session_factory()
    try:
        estate_id = sample_data["estates"][0]["estate_id"]
        stage_a = EstateStage(estate_id=estate_id, name="Stage 1")
        stage_b = EstateStage(estate_id=estate_id, name="Stage 2")
        session.add_all([stage_a, stage_b])
        session.flush()

        statuses = [
            LotStatus.AVAILABLE,
            LotStatus.AVAILABLE,
            LotStatus.HOLD,
            LotStatus.SOLD,
            LotStatus.UNAVAILABLE,
        ]
        stage_a_lots = []
        stage_b_lots = []
        for i, st in enumerate(statuses, start=1):
            lot_a = StageLot(
                stage_id=stage_a.stage_id,
                lot_number=f"A{i}",
                status=st,
                source=Source.MANUAL,
            )
            lot_b = StageLot(
                stage_id=stage_b.stage_id,
                lot_number=f"B{i}",
                status=st,
                source=Source.MANUAL,
            )
            session.add_all([lot_a, lot_b])
            stage_a_lots.append(lot_a)
            stage_b_lots.append(lot_b)
        session.commit()

        return {
            "estate_id": estate_id,
            "stage_a_id": stage_a.stage_id,
            "stage_b_id": stage_b.stage_id,
            "stage_a_lot_ids": [lot.lot_id for lot in stage_a_lots],
            "stage_b_lot_ids": [lot.lot_id for lot in stage_b_lots],
            "statuses": [s.value for s in statuses],
        }
    finally:
        session.close()


@pytest.fixture()
def tmp_storage(tmp_path, monkeypatch):
    """Redirect the default StorageService to a temporary directory for this test."""
    from hlp.shared import storage_service as ss

    new_service = ss.StorageService(base_path=str(tmp_path))
    monkeypatch.setattr(ss, "_default_service", new_service)

    yield tmp_path

    monkeypatch.setattr(ss, "_default_service", None)


SECOND_USER = {
    "email": "second@it.example.com",
    "password": "Second1234!",
    "first_name": "Second",
    "last_name": "User",
    "job_title": "Sales",
    "roles": [UserRoleType.SALES],
}


@pytest.fixture()
def second_user(_session_factory):
    """Create a second user for isolation tests (independent of seeded_users)."""
    session: Session = _session_factory()
    try:
        profile = user_service.create_user_with_roles(
            session,
            email=SECOND_USER["email"],
            password=SECOND_USER["password"],
            first_name=SECOND_USER["first_name"],
            last_name=SECOND_USER["last_name"],
            job_title=SECOND_USER["job_title"],
            roles=SECOND_USER["roles"],
        )
        session.commit()
        return {
            "profile_id": profile.profile_id,
            "email": profile.email,
            "password": SECOND_USER["password"],
        }
    finally:
        session.close()


@pytest.fixture()
def second_user_token(client: TestClient, second_user) -> str:
    return _login(client, second_user["email"], second_user["password"])


@pytest.fixture()
def second_user_headers(second_user_token: str) -> dict[str, str]:
    return auth_header(second_user_token)


# -----------------------------------------------------------------------------
# Sprint 3 fixtures: richer dataset for Land Search Interface tests.
# -----------------------------------------------------------------------------


@pytest.fixture()
def search_seed_data(_session_factory):
    """Seed 3 estates (2 VIC, 1 NSW) x 2 stages x 5 lots with varied attributes."""
    from datetime import date
    from decimal import Decimal

    from hlp.models.developer import Developer
    from hlp.models.enums import LotStatus, Source
    from hlp.models.estate import Estate
    from hlp.models.estate_stage import EstateStage
    from hlp.models.region import Region
    from hlp.models.stage_lot import StageLot

    session: Session = _session_factory()
    try:
        region_metro = Region(name="Metro")
        region_growth = Region(name="Growth Corridor")
        session.add_all([region_metro, region_growth])
        session.flush()

        dev_alpha = Developer(developer_name="AlphaDev")
        dev_beta = Developer(developer_name="BetaBuild")
        session.add_all([dev_alpha, dev_beta])
        session.flush()

        estate_a = Estate(
            developer_id=dev_alpha.developer_id,
            region_id=region_metro.region_id,
            estate_name="Acacia Rise",
            suburb="Tarneit",
            state="VIC",
            postcode="3029",
            active=True,
        )
        estate_b = Estate(
            developer_id=dev_alpha.developer_id,
            region_id=region_growth.region_id,
            estate_name="Banksia Park",
            suburb="Werribee",
            state="VIC",
            postcode="3030",
            active=True,
        )
        estate_c = Estate(
            developer_id=dev_beta.developer_id,
            region_id=region_growth.region_id,
            estate_name="Cedar Grove",
            suburb="Oran Park",
            state="NSW",
            postcode="2570",
            active=True,
        )
        session.add_all([estate_a, estate_b, estate_c])
        session.flush()

        statuses_cycle = [
            LotStatus.AVAILABLE,
            LotStatus.AVAILABLE,
            LotStatus.HOLD,
            LotStatus.SOLD,
            LotStatus.UNAVAILABLE,
        ]

        estates = [
            ("A", estate_a),
            ("B", estate_b),
            ("C", estate_c),
        ]
        lot_ids_by_status: dict[str, list[int]] = {s.value: [] for s in LotStatus}
        all_lot_ids: list[int] = []
        stage_ids: list[int] = []
        for letter, estate in estates:
            for stage_num in (1, 2):
                stage = EstateStage(
                    estate_id=estate.estate_id, name=f"Stage {stage_num}"
                )
                session.add(stage)
                session.flush()
                stage_ids.append(stage.stage_id)
                price_options = [
                    Decimal("300000.00"),
                    Decimal("350000.00"),
                    Decimal("400000.00"),
                    Decimal("450000.00"),
                    None,
                ]
                size_options = [
                    Decimal("350.00"),
                    Decimal("400.00"),
                    Decimal("450.00"),
                    Decimal("500.00"),
                    Decimal("550.00"),
                ]
                frontage_options = [
                    Decimal("10.00"),
                    Decimal("12.50"),
                    Decimal("14.00"),
                    Decimal("16.00"),
                    Decimal("18.00"),
                ]
                depth_options = [
                    Decimal("28.00"),
                    Decimal("30.00"),
                    Decimal("32.00"),
                    Decimal("34.00"),
                    Decimal("36.00"),
                ]
                title_dates = [
                    date(2026, 3, 1),
                    date(2026, 6, 1),
                    date(2026, 9, 1),
                    date(2026, 12, 1),
                    date(2027, 3, 1),
                ]
                for i in range(5):
                    lot = StageLot(
                        stage_id=stage.stage_id,
                        lot_number=f"{letter}{stage_num}-{i + 1}",
                        frontage=frontage_options[i],
                        depth=depth_options[i],
                        size_sqm=size_options[i],
                        corner_block=(i == 0),
                        land_price=price_options[i],
                        status=statuses_cycle[i],
                        source=Source.MANUAL,
                        title_date=title_dates[i],
                    )
                    session.add(lot)
                    session.flush()
                    lot_ids_by_status[statuses_cycle[i].value].append(lot.lot_id)
                    all_lot_ids.append(lot.lot_id)
        session.commit()

        return {
            "regions": {
                "metro": region_metro.region_id,
                "growth": region_growth.region_id,
            },
            "developers": {
                "alpha": dev_alpha.developer_id,
                "beta": dev_beta.developer_id,
            },
            "estates": {
                "acacia": estate_a.estate_id,
                "banksia": estate_b.estate_id,
                "cedar": estate_c.estate_id,
            },
            "stage_ids": stage_ids,
            "total_lots": len(all_lot_ids),
            "lot_ids_by_status": lot_ids_by_status,
        }
    finally:
        session.close()


def upload_file(
    client: TestClient,
    estate_id: int,
    filename: str,
    content_type: str,
    content: bytes,
    headers: dict[str, str] | None = None,
    stage_id: int | None = None,
    description: str | None = None,
):
    """Helper: POST a document to the estate upload endpoint."""
    params = []
    if stage_id is not None:
        params.append(f"stage_id={stage_id}")
    if description is not None:
        params.append(f"description={description}")
    suffix = ("?" + "&".join(params)) if params else ""
    return client.post(
        f"/api/estates/{estate_id}/documents{suffix}",
        files={"file": (filename, content, content_type)},
        headers=headers or {},
    )

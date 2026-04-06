"""Shared test fixtures and SQLite-compatible engine helpers.

Sprint 1 only touches 5 tables (profiles, user_roles, regions, developers,
estates). Other models in hlp.models use PostgreSQL-specific column types
(JSONB, ARRAY) that SQLite can't create. We therefore restrict
``Base.metadata.create_all`` to the Sprint 1 tables so tests can run against
an in-memory SQLite database without Docker.

Running the tests
-----------------
    pytest tests/unit/           # fast pure-Python + in-memory DB unit tests
    pytest tests/integration/    # FastAPI TestClient + SQLite integration tests
    pytest tests/                # everything

Neither tier requires a Docker daemon. When later sprints introduce
JSONB/ARRAY columns to tables that tests need, swap the SQLite engine fixture
for a testcontainers Postgres one (``pip install 'testcontainers[postgres]'``).
"""
from __future__ import annotations

from collections.abc import Iterator

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker  # noqa: F401  (Session re-exported)
from sqlalchemy.pool import StaticPool

# Import all Sprint 1 models so they register on Base.metadata.
import hlp.models  # noqa: F401
from hlp.database import Base

SPRINT1_TABLES = (
    "profiles",
    "user_roles",
    "regions",
    "developers",
    "estates",
    "estate_stages",
    # Sprint 2 additions
    "stage_lots",
    "status_history",
    "estate_documents",
    # Sprint 3 additions
    "filter_presets",
    # Sprint 4 additions
    "clash_rules",
    "house_packages",
    # Sprint 5 additions
    "pricing_rule_categories",
    "pricing_templates",
    "global_pricing_rules",
    "stage_pricing_rules",
    # Sprint 6 additions
    "pricing_requests",
    "notifications",
)


def _sprint1_metadata_tables():
    return [Base.metadata.tables[name] for name in SPRINT1_TABLES]


@pytest.fixture(scope="session")
def engine() -> Iterator[Engine]:
    """In-memory SQLite engine with Sprint 1 tables created."""
    eng = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,  # share a single connection so schema persists
        future=True,
    )

    # SQLite requires FK enforcement to be enabled explicitly for cascade deletes.
    @event.listens_for(eng, "connect")
    def _fk_pragma(dbapi_connection, _):  # pragma: no cover - trivial
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(eng, tables=_sprint1_metadata_tables())
    try:
        yield eng
    finally:
        Base.metadata.drop_all(eng, tables=_sprint1_metadata_tables())
        eng.dispose()


@pytest.fixture()
def db_session(engine: Engine) -> Iterator[Session]:
    """Fresh session per test; truncates Sprint 1 tables after each test."""
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()
        # Clean tables in FK-safe order.
        with engine.begin() as conn:
            for table in (
                "notifications",
                "pricing_requests",
                "stage_pricing_rules",
                "global_pricing_rules",
                "pricing_rule_categories",
                "pricing_templates",
                "house_packages",
                "clash_rules",
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

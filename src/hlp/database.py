"""SQLAlchemy engine and session factory."""

from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from hlp.config import get_settings


class Base(DeclarativeBase):
    """Base class for all ORM models."""

    pass


@lru_cache
def get_engine() -> Engine:
    url = get_settings().database_url
    connect_args: dict = {}
    # psycopg2 supports connect_timeout; applies to Postgres only
    if url.startswith("postgresql"):
        connect_args["connect_timeout"] = 10
    return create_engine(url, echo=False, pool_pre_ping=True, connect_args=connect_args)


def get_session_factory() -> sessionmaker[Session]:
    return sessionmaker(bind=get_engine(), autocommit=False, autoflush=False)


def get_db():
    """FastAPI dependency that yields a database session."""
    session = get_session_factory()()
    try:
        yield session
    finally:
        session.close()

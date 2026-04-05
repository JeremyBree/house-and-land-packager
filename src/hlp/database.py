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
    return create_engine(get_settings().database_url, echo=False)


def get_session_factory() -> sessionmaker[Session]:
    return sessionmaker(bind=get_engine(), autocommit=False, autoflush=False)


def get_db():
    """FastAPI dependency that yields a database session."""
    session = get_session_factory()()
    try:
        yield session
    finally:
        session.close()

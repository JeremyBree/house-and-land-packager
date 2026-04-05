"""FastAPI application factory."""

import logging
import sys
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

import hlp.models  # noqa: F401  # register all models on Base.metadata
from hlp.config import get_settings
from hlp.database import Base, get_db, get_engine

# Configure logging to stdout for Railway
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: create tables on startup."""
    logger.info("Application starting up...")
    try:
        engine = get_engine()
        logger.info("Connecting to database and creating tables...")
        Base.metadata.create_all(engine)
        logger.info("Database tables created/verified successfully (19 tables)")
    except Exception as exc:
        # Don't crash on startup if DB is unavailable — health check will report it
        logger.warning("Could not initialize database on startup: %s", exc)
    logger.info("Application startup complete")
    yield
    logger.info("Application shutting down")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()

    application = FastAPI(
        title="House and Land Packager",
        version="0.1.0",
        description="House & Land Package Pricing, Clash Management, and Land Data Aggregation",
        lifespan=lifespan,
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins.split(","),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @application.get("/api/health")
    async def health_check():
        return {"status": "healthy", "version": "0.1.0"}

    @application.get("/api/health/db")
    async def db_health_check(db: Session = Depends(get_db)):
        """Verify database connectivity and count known tables."""
        try:
            db.execute(text("SELECT 1"))
            result = db.execute(
                text(
                    "SELECT COUNT(*) FROM information_schema.tables "
                    "WHERE table_schema = 'public'"
                )
            ).scalar()
            return {"status": "connected", "tables": result}
        except Exception as exc:
            return {"status": "error", "detail": str(exc)}

    return application


app = create_app()

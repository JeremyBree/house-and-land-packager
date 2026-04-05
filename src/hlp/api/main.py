"""FastAPI application factory."""

import logging
import sys
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

import hlp.models  # noqa: F401  # register all models on Base.metadata
from hlp.api.routers import auth as auth_router
from hlp.api.routers import developers as developers_router
from hlp.api.routers import estates as estates_router
from hlp.api.routers import regions as regions_router
from hlp.api.routers import users as users_router
from hlp.config import get_settings
from hlp.database import Base, get_db, get_engine
from hlp.shared.exceptions import (
    AuthenticationError,
    DuplicateEmailError,
    HLPError,
    MinRolesRequiredError,
    NotAuthorizedError,
    NotFoundError,
    UserNotFoundError,
)

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


def _error_response(status_code: int, detail: str, code: str) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"detail": detail, "code": code})


def _register_exception_handlers(application: FastAPI) -> None:
    @application.exception_handler(AuthenticationError)
    async def _auth_err(_: Request, exc: AuthenticationError):
        return _error_response(401, str(exc) or "Authentication failed", "authentication_error")

    @application.exception_handler(NotAuthorizedError)
    async def _notauth_err(_: Request, exc: NotAuthorizedError):
        return _error_response(403, str(exc) or "Not authorized", "not_authorized")

    @application.exception_handler(DuplicateEmailError)
    async def _dup_err(_: Request, exc: DuplicateEmailError):
        return _error_response(409, str(exc), "duplicate_email")

    @application.exception_handler(UserNotFoundError)
    async def _user_nf(_: Request, exc: UserNotFoundError):
        return _error_response(404, str(exc), "user_not_found")

    @application.exception_handler(NotFoundError)
    async def _nf(_: Request, exc: NotFoundError):
        return _error_response(404, str(exc), "not_found")

    @application.exception_handler(MinRolesRequiredError)
    async def _min_roles(_: Request, exc: MinRolesRequiredError):
        return _error_response(400, str(exc), "min_roles_required")

    @application.exception_handler(HLPError)
    async def _hlp_err(_: Request, exc: HLPError):
        return _error_response(500, str(exc) or "Server error", "server_error")


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

    _register_exception_handlers(application)

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

    application.include_router(auth_router.router)
    application.include_router(users_router.router)
    application.include_router(regions_router.router)
    application.include_router(developers_router.router)
    application.include_router(estates_router.router)

    return application


app = create_app()

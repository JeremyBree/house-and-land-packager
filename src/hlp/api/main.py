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
from hlp.api.routers import documents as documents_router
from hlp.api.routers import estates as estates_router
from hlp.api.routers import files as files_router
from hlp.api.routers import lots as lots_router
from hlp.api.routers import regions as regions_router
from hlp.api.routers import stages as stages_router
from hlp.api.routers import users as users_router
from hlp.config import get_settings
from hlp.database import Base, get_db, get_engine
from hlp.shared.exceptions import (
    AuthenticationError,
    DocumentNotFoundError,
    DuplicateEmailError,
    FileTooLargeError,
    HLPError,
    InvalidCsvError,
    InvalidStatusTransitionError,
    LotNotFoundError,
    MinRolesRequiredError,
    NotAuthorizedError,
    NotFoundError,
    StageNotFoundError,
    UnsupportedFileTypeError,
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
    """Application lifespan: create tables and seed on startup if empty."""
    logger.info("Application starting up...")
    try:
        engine = get_engine()
        logger.info("Connecting to database and creating tables...")
        Base.metadata.create_all(engine)
        logger.info("Database tables created/verified successfully (19 tables)")
        # Auto-seed on startup (idempotent for PoC)
        from hlp.database import get_session_factory
        from hlp.models.estate_stage import EstateStage
        from hlp.models.profile import Profile

        session = get_session_factory()()
        try:
            profile_count = session.query(Profile).count()
            stage_count = session.query(EstateStage).count()
            if profile_count == 0 or stage_count == 0:
                logger.info(
                    "Running dev seed (profiles=%d, stages=%d)...",
                    profile_count,
                    stage_count,
                )
                from hlp.seeds.dev_seed import seed_dev

                seed_dev(session)
                session.commit()
                logger.info("Dev seed complete")
            else:
                logger.info(
                    "Database already seeded (%d profiles, %d stages), skipping",
                    profile_count,
                    stage_count,
                )
        finally:
            session.close()
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

    @application.exception_handler(StageNotFoundError)
    async def _stage_nf(_: Request, exc: StageNotFoundError):
        return _error_response(404, str(exc), "stage_not_found")

    @application.exception_handler(LotNotFoundError)
    async def _lot_nf(_: Request, exc: LotNotFoundError):
        return _error_response(404, str(exc), "lot_not_found")

    @application.exception_handler(DocumentNotFoundError)
    async def _doc_nf(_: Request, exc: DocumentNotFoundError):
        return _error_response(404, str(exc), "document_not_found")

    @application.exception_handler(NotFoundError)
    async def _nf(_: Request, exc: NotFoundError):
        return _error_response(404, str(exc), "not_found")

    @application.exception_handler(InvalidStatusTransitionError)
    async def _bad_transition(_: Request, exc: InvalidStatusTransitionError):
        return _error_response(400, str(exc), "invalid_status_transition")

    @application.exception_handler(InvalidCsvError)
    async def _bad_csv(_: Request, exc: InvalidCsvError):
        return _error_response(422, str(exc), "invalid_csv")

    @application.exception_handler(UnsupportedFileTypeError)
    async def _bad_file_type(_: Request, exc: UnsupportedFileTypeError):
        return _error_response(415, str(exc), "unsupported_file_type")

    @application.exception_handler(FileTooLargeError)
    async def _file_too_large(_: Request, exc: FileTooLargeError):
        return _error_response(413, str(exc), "file_too_large")

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
    application.include_router(stages_router.estates_scoped_router)
    application.include_router(stages_router.stages_router)
    application.include_router(lots_router.stages_scoped_router)
    application.include_router(lots_router.lots_router)
    application.include_router(documents_router.estate_scoped_router)
    application.include_router(documents_router.docs_router)
    application.include_router(files_router.router)

    return application


app = create_app()

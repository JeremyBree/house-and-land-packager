"""FastAPI application factory."""

import hashlib
import logging
import os
import sys
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from sqlalchemy.orm import Session

import hlp.models  # noqa: F401  # register all models on Base.metadata
from hlp.api.routers import auth as auth_router
from hlp.api.routers import clash_rules as clash_rules_router
from hlp.api.routers import configurations as configurations_router
from hlp.api.routers import conflicts as conflicts_router
from hlp.api.routers import dashboard as dashboard_router
from hlp.api.routers import developers as developers_router
from hlp.api.routers import documents as documents_router
from hlp.api.routers import estates as estates_router
from hlp.api.routers import files as files_router
from hlp.api.routers import filter_presets as filter_presets_router
from hlp.api.routers import import_data as import_data_router
from hlp.api.routers import ingestion_logs as ingestion_logs_router
from hlp.api.routers import lot_search as lot_search_router
from hlp.api.routers import lots as lots_router
from hlp.api.routers import notifications as notifications_router
from hlp.api.routers import packages as packages_router
from hlp.api.routers import pricing_requests as pricing_requests_router
from hlp.api.routers import pricing_rules as pricing_rules_router
from hlp.api.routers import pricing_templates as pricing_templates_router
from hlp.api.routers import regions as regions_router
from hlp.api.routers import stages as stages_router
from hlp.api.routers import users as users_router
from hlp.api.middleware.site_auth import SiteAuthMiddleware, _PASSWORD_PAGE, _hash_password
from hlp.config import get_settings
from hlp.database import Base, get_db, get_engine

STATIC_DIR = "/app/static"
from hlp.shared.exceptions import (
    AuthenticationError,
    CategoryNotFoundError,
    ClashRuleNotFoundError,
    ClashViolationError,
    DocumentNotFoundError,
    DuplicateClashRuleError,
    DuplicateEmailError,
    DuplicatePresetNameError,
    ExportTooLargeError,
    FileTooLargeError,
    FilterPresetNotFoundError,
    HLPError,
    InvalidCsvError,
    InvalidStatusTransitionError,
    InvalidTemplateError,
    LotNotFoundError,
    MinRolesRequiredError,
    NotAuthorizedError,
    NotFoundError,
    PackageNotFoundError,
    PricingRequestNotFoundError,
    PricingRuleNotFoundError,
    StageNotFoundError,
    TemplateNotFoundError,
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
        # Auto-seed on startup (idempotent for PoC — always run, seed_dev skips existing)
        from hlp.database import get_session_factory

        session = get_session_factory()()
        try:
            logger.info("Running idempotent dev seed...")
            from hlp.seeds.dev_seed import seed_dev

            seed_dev(session)
            session.commit()
            logger.info("Dev seed complete")
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

    @application.exception_handler(ClashViolationError)
    async def _clash_violation(_: Request, exc: ClashViolationError):
        return JSONResponse(
            status_code=409,
            content={
                "detail": str(exc),
                "code": "clash_violation",
                "violations": exc.violations,
            },
        )

    @application.exception_handler(PricingRequestNotFoundError)
    async def _pricing_req_nf(_: Request, exc: PricingRequestNotFoundError):
        return _error_response(404, str(exc), "pricing_request_not_found")

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

    @application.exception_handler(FilterPresetNotFoundError)
    async def _preset_nf(_: Request, exc: FilterPresetNotFoundError):
        return _error_response(404, str(exc), "filter_preset_not_found")

    @application.exception_handler(DuplicatePresetNameError)
    async def _dup_preset(_: Request, exc: DuplicatePresetNameError):
        return _error_response(409, str(exc), "duplicate_preset_name")

    @application.exception_handler(ExportTooLargeError)
    async def _export_too_large(_: Request, exc: ExportTooLargeError):
        return _error_response(413, str(exc), "export_too_large")

    @application.exception_handler(ClashRuleNotFoundError)
    async def _clash_nf(_: Request, exc: ClashRuleNotFoundError):
        return _error_response(404, str(exc), "clash_rule_not_found")

    @application.exception_handler(PackageNotFoundError)
    async def _package_nf(_: Request, exc: PackageNotFoundError):
        return _error_response(404, str(exc), "package_not_found")

    @application.exception_handler(DuplicateClashRuleError)
    async def _dup_clash(_: Request, exc: DuplicateClashRuleError):
        return _error_response(409, str(exc), "duplicate_clash_rule")

    @application.exception_handler(TemplateNotFoundError)
    async def _template_nf(_: Request, exc: TemplateNotFoundError):
        return _error_response(404, str(exc), "template_not_found")

    @application.exception_handler(InvalidTemplateError)
    async def _bad_template(_: Request, exc: InvalidTemplateError):
        return _error_response(422, str(exc), "invalid_template")

    @application.exception_handler(PricingRuleNotFoundError)
    async def _rule_nf(_: Request, exc: PricingRuleNotFoundError):
        return _error_response(404, str(exc), "pricing_rule_not_found")

    @application.exception_handler(CategoryNotFoundError)
    async def _cat_nf(_: Request, exc: CategoryNotFoundError):
        return _error_response(404, str(exc), "category_not_found")

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

    # Site-wide password gate (before everything else; CORS must wrap it).
    application.add_middleware(SiteAuthMiddleware)

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
    application.include_router(lot_search_router.router)
    application.include_router(filter_presets_router.router)
    application.include_router(clash_rules_router.estate_scoped_router)
    application.include_router(clash_rules_router.stage_scoped_router)
    application.include_router(clash_rules_router.estate_stage_router)
    application.include_router(clash_rules_router.rules_router)
    application.include_router(packages_router.router)
    application.include_router(conflicts_router.router)
    application.include_router(pricing_templates_router.router)
    application.include_router(pricing_rules_router.categories_router)
    application.include_router(pricing_rules_router.rules_router)
    application.include_router(pricing_requests_router.router)
    application.include_router(notifications_router.router)
    application.include_router(dashboard_router.router)
    application.include_router(configurations_router.router)
    application.include_router(ingestion_logs_router.router)
    application.include_router(import_data_router.router)

    # ---- Site password endpoint ------------------------------------------------
    @application.post("/site-auth")
    async def site_auth(request: Request, password: str = Form(...)):
        """Validate the site-wide password and set an access cookie."""
        if password == settings.site_password:
            response = RedirectResponse(url="/", status_code=302)
            is_secure = request.url.scheme == "https"
            response.set_cookie(
                key="site_access",
                value=_hash_password(password),
                httponly=True,
                secure=is_secure,
                samesite="lax",
                max_age=86400 * 30,  # 30 days
            )
            return response
        # Wrong password -- re-render the form with an error.
        error_html = '<p style="color:#dc2626;font-size:13px;margin:1rem 0 0;">Incorrect password.</p>'
        return HTMLResponse(
            content=_PASSWORD_PAGE.replace("{error_html}", error_html),
            status_code=403,
        )

    # ---- Serve React SPA (only when built frontend is present) -----------------
    if os.path.isdir(STATIC_DIR):
        application.mount(
            "/assets",
            StaticFiles(directory=os.path.join(STATIC_DIR, "assets")),
            name="static-assets",
        )

        @application.get("/{full_path:path}")
        async def serve_spa(full_path: str):
            """Serve static files or fall back to index.html for SPA routing."""
            file_path = os.path.join(STATIC_DIR, full_path)
            if os.path.isfile(file_path):
                return FileResponse(file_path)
            return FileResponse(os.path.join(STATIC_DIR, "index.html"))

    return application


app = create_app()

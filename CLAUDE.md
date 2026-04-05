# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**House and Land Packager** — a web platform with two subsystems:

1. **Land Data Aggregation** — AI agents scrape developer websites, portals, emails, and PDFs to collect residential land lot data automatically.
2. **House & Land Package Management** — Pricing request workflow, clash rule enforcement, Excel template generation, and package management for two brands: Hermitage Homes and Kingsbridge Homes.

The authoritative project specification is `Readme.md` (v3.0). Reference materials are in `/Reference/` (BRD, Packaging Requirements doc, UI screenshots, HTML mockup).

## Architecture

**Python-first modular monolith** deployed as a single Railway service (PoC). Azure is the future production target.

- **Backend:** FastAPI (Python 3.12+), SQLAlchemy 2.0, Alembic, APScheduler
- **Frontend:** React + Vite + shadcn/ui + Tailwind CSS, TanStack Table
- **Database:** PostgreSQL (Railway plugin, connected via `DATABASE_URL`)
- **File Storage:** Railway Volume mounted at `/data/storage/`
- **Auth:** Self-managed JWT + bcrypt, role-based (Admin, Pricing, Sales, Requester)
- **LLM:** Anthropic Claude API (Sonnet) for structured data extraction
- **Excel:** openpyxl for template management and spreadsheet generation

The API service consolidates REST API, packaging engine, agent orchestrator, and scheduled agents (APScheduler) into one process to minimise Railway costs.

### Key Backend Modules

- `src/hlp/api/` — FastAPI routers, Pydantic schemas, middleware
- `src/hlp/models/` — SQLAlchemy ORM models (15 tables)
- `src/hlp/repositories/` — Data access layer with typed query methods
- `src/hlp/agents/` — Ingestion agents (email, scraper, portal, PDF) + AI extraction pipeline
- `src/hlp/orchestrator/` — Scheduler, dispatcher, lot lifecycle engine, conflict resolution
- `src/hlp/packaging/` — Spreadsheet generator, clash validator, pricing rule evaluator, package importer
- `src/hlp/shared/` — Auth, logging, storage abstraction, CSV/XLSX export

### Key Frontend Modules

- `frontend/src/components/lsi/` — Land Search Interface (filter panel, results table, lot detail)
- `frontend/src/components/pricing/` — Pricing request form and tracking
- `frontend/src/components/estates/` — Estate, stage, lot, clash rule management
- `frontend/src/components/packages/` — Package browsing and management
- `frontend/src/components/admin/` — User management, pricing templates, pricing rules

### Data Model

15 tables: `regions`, `developers`, `estates`, `estate_stages`, `stage_lots`, `status_history`, `house_packages`, `clash_rules`, `pricing_requests`, `pricing_templates`, `global_pricing_rules`, `stage_pricing_rules`, `pricing_rule_categories`, `profiles`, `user_roles`, `notifications`, `estate_documents`, `ingestion_log`, `configuration`.

Lot uniqueness is `(stage_id, lot_number)`. Clash rules are scoped to `(estate_id, stage_id)`. Pricing rules can be global (brand-wide) or stage-specific.

## Commands

```bash
# Local development
docker compose up -d                          # Start PostgreSQL
source .venv/bin/activate                     # Activate Python venv
pip install -e ".[dev]"                       # Install with dev deps
alembic upgrade head                          # Run migrations
python -m hlp.seeds.dev_seed                  # Seed dev data
uvicorn hlp.api.main:app --reload --port 8000 # Start API

# Frontend
cd frontend && npm install && npm run dev     # Vite dev server on :5173

# Testing
pytest tests/unit/                            # Unit tests only
pytest tests/unit/test_clash_validator.py      # Single test file
pytest tests/integration/                     # Integration (needs Docker)
pytest tests/e2e/                             # E2E (needs API + frontend running)
pytest -x -v tests/unit/test_lifecycle.py::test_absent_marks_unavailable  # Single test

# Linting & type checking
ruff check src/ tests/                        # Lint
ruff format src/ tests/                       # Format
mypy src/hlp/                                 # Type check

# Railway deployment
railway login && railway link                 # First-time setup
railway up                                    # Manual deploy
# Auto-deploy triggers on push to main

# Database
alembic revision --autogenerate -m "description"  # New migration
alembic upgrade head                              # Apply migrations
alembic downgrade -1                              # Rollback one
```

## Technical Conventions

- **SQLAlchemy 2.0** style: use `mapped_column()`, type-annotated models, `Mapped[]` types
- **Pydantic v2** for all API schemas and validation
- **All datetimes in UTC** — application layer converts to AEST/AEDT for display
- **No physical deletes on lots** — use `status = Unavailable` (soft delete)
- **Credentials never stored in DB** — `Configuration.credentials_ref` holds env var names only
- **File storage abstraction** — `src/hlp/shared/storage.py` wraps Railway Volume paths; designed for future Azure Blob migration
- **structlog** for JSON-formatted structured logging

## Business Logic

### Clash Rules
- Scoped to estate + stage, not universal
- Bidirectional: if lot A cannot clash with B, then B cannot clash with A
- Two-pass validation at pricing request submission: (1) within the request, (2) against existing packages
- A clash is triggered when two restricted lots share the same design AND facade (case-insensitive)

### Pricing Request Flow
- Sales submits → spreadsheet auto-generated from brand template (openpyxl) → pricing team uploads completed sheet → packages extracted and imported into DB
- Conditional pricing rules evaluated against a `RequestContext` built from form toggles (corner_block, is_kdrb, building_crossover, etc.)

### Lot Status Lifecycle
- After each ingestion: present in feed → Available; absent from feed → Unavailable
- Multi-source rule: only mark Unavailable when absent from ALL sources
- Status values: Available, Unavailable, Hold, Deposit Taken, Sold

### Brand-Specific Logic
- **Hermitage Homes:** requires BDM, Wholesale Group, Garage Side per lot
- **Kingsbridge Homes:** has Custom House Design toggle per lot
- Each brand has its own pricing template with separate cell mappings and data validations

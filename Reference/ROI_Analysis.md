# ROI Analysis — Claude Code vs Traditional Development Team

**Date:** 2026-04-08
**Project:** House and Land Packager — Changes Sprint
**Scope:** 5 change requests + Import Data UI (see `changes.md`)

---

## What Was Delivered

| Metric | Count |
|---|---|
| Files created/modified | ~67 |
| Lines of code added | ~9,500 |
| Backend API endpoints added | ~65 new routes |
| Frontend admin pages | 15 new pages |
| Frontend forms converted | 3 existing forms |
| New database models | 2 (PendingExtraction, ApiKey) |
| Alembic migrations | 2 |
| New services/modules | 4 (pdf_extractor, pdf_ingestion_service, api_key_service, import UI) |

**Claude Code elapsed time: ~3 hours**

---

## Human Effort Estimate (Senior Team)

### Backend Engineer (Senior Python/FastAPI)

| Work Item | Hours |
|---|---|
| Change 1 — Fix packages endpoint to return names | 1.5 |
| Change 2 — No backend changes needed | 0 |
| Change 3 — CRUD routers for 14 reference tables (6 routers, 14 schema files, 7 repositories) | 28 |
| Change 4 — PDF ingestion model, migration, extraction service, approval service, router | 20 |
| Change 5 — API key model, auth middleware, key service, external ingestion router with upsert logic | 18 |
| Import data endpoint (already existed, no work) | 0 |
| **Backend subtotal** | **67.5 hrs** |

### Frontend Engineer (Senior React/TypeScript)

| Work Item | Hours |
|---|---|
| Change 1 — Update types + column rendering | 1 |
| Change 2 — Convert 3 forms to cascading dropdowns, new API client, ad-hoc toggle | 12 |
| Change 3 — 15 admin CRUD pages with form dialogs, tables, delete confirmations | 48 |
| Change 4 — PDF ingestion page with drag-drop upload, extraction review, approve/reject | 10 |
| Change 5 — API keys admin page with create/copy-key/revoke | 8 |
| Import data page with drag-drop upload and results display | 4 |
| Route + sidebar registration for all pages | 2 |
| **Frontend subtotal** | **85 hrs** |

### Tech Lead / Architect

| Work Item | Hours |
|---|---|
| Requirements analysis — read changes.md, ask clarifying questions | 2 |
| Sprint planning — break into 6 sprints, identify dependencies | 3 |
| API design — endpoint structure, auth model, external API scoping | 4 |
| Architecture decisions — lazy imports, approval workflow, upsert patterns | 3 |
| Code review (6 sprints worth) | 8 |
| Deployment debugging (anthropic dependency issue) | 1 |
| **Tech Lead subtotal** | **21 hrs** |

### Business Analyst

| Work Item | Hours |
|---|---|
| Requirements refinement — dropdown behaviour, PDF extraction fields, API scoping | 4 |
| Acceptance criteria per change (5 changes) | 6 |
| UAT coordination | 3 |
| **BA subtotal** | **13 hrs** |

### QA Engineer

| Work Item | Hours |
|---|---|
| Change 1 & 2 — Test packages display, all dropdown forms (3 forms x 3 paths each) | 6 |
| Change 3 — Test 15 admin CRUD pages (create, edit, delete, validation per page) | 24 |
| Change 4 — Test PDF upload, extraction review, approve/reject workflows | 6 |
| Change 5 — Test API key create, revoke, external API auth, ingestion endpoints | 6 |
| Import data — Test upload, results display, error cases | 2 |
| Regression testing | 4 |
| **QA subtotal** | **48 hrs** |

### DevOps

| Work Item | Hours |
|---|---|
| Dependency management, Dockerfile updates | 1.5 |
| Migration deployment coordination | 1 |
| Deployment debugging + rollback if needed | 1.5 |
| **DevOps subtotal** | **4 hrs** |

---

## Summary: Total Human Effort

| Role | Hours | Day Equiv (8hr) | Typical AU Day Rate | Cost |
|---|---|---|---|---|
| Senior Backend Engineer | 67.5 | 8.4 days | $1,200/day | $10,125 |
| Senior Frontend Engineer | 85 | 10.6 days | $1,200/day | $12,750 |
| Tech Lead / Architect | 21 | 2.6 days | $1,600/day | $4,200 |
| Business Analyst | 13 | 1.6 days | $1,000/day | $1,625 |
| QA Engineer | 48 | 6.0 days | $900/day | $5,400 |
| DevOps Engineer | 4 | 0.5 days | $1,200/day | $600 |
| **Total** | **238.5 hrs** | **29.8 days** | | **$34,700** |

---

## ROI Model Inputs

| Metric | Value |
|---|---|
| **Human effort (calendar)** | ~6 weeks (with parallelism, handoffs, standups, context-switching) |
| **Human effort (person-hours)** | 238.5 hours |
| **Human cost estimate** | ~$34,700 AUD |
| **Claude Code time** | ~3 hours wall-clock |
| **Claude Code API cost** (estimated) | ~$50-80 USD (~$80-120 AUD) |
| **Effort reduction** | ~98.7% |
| **Cost reduction** | ~99.7% |
| **Speed improvement** | ~80x faster (6 weeks to 3 hours) |

### Long-Term Savings Model

| Scenario | Annual Human Cost | Annual with Claude Code | Savings |
|---|---|---|---|
| 1 sprint like this per month | $416,400 | ~$1,500 + subscription | $414,900 |
| 1 sprint like this per quarter | $138,800 | ~$500 + subscription | $138,300 |
| One-off project | $34,700 | ~$120 | $34,580 |

### Caveats for the ROI Model

- These estimates assume **senior** staff who don't need ramp-up time on the stack
- Real calendar time is longer than person-hours due to context switching, meetings, code review cycles, and handoffs between roles
- Claude Code output still needs human review, UAT, and production monitoring — the QA and BA effort doesn't fully disappear, it shifts to review
- The AI-generated code is production-shaped but may need refinement under real user load (edge cases, performance tuning)
- Highest ROI is on **repetitive CRUD patterns** (Change 3 was 14 near-identical admin pages) — this is where AI has the biggest multiplier

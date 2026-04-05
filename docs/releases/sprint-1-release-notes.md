# Sprint 1 Release Notes

**Release date:** 2026-04-05
**Environment:** Railway PoC
**URL:** https://house-and-land-packager-production.up.railway.app
**Repository:** https://github.com/JeremyBree/house-and-land-packager

Sprint 1 establishes the authentication layer and the core entity
management surface that every later sprint builds on.

## What's New (User-Facing)

- **Login and protected layout.** A React SPA with a login page, protected
  routes, and a role-aware sidebar.
- **Estate management.** Authenticated users can browse estates with
  search, filters (developer, region, active), and pagination. Admins can
  create, edit, and soft-delete estates.
- **Admin pages.**
  - **Users**: create users, assign/replace roles, update names, delete.
  - **Regions**: full CRUD.
  - **Developers**: full CRUD.
- **Role-based access.** Four roles — admin, pricing, sales, requester —
  enforced on every protected endpoint.

## Technical Additions

### Backend

- FastAPI application wired with CORS, structured JSON logging
  (structlog), and consistent `{detail, code}` error responses.
- JWT auth (HS256) with 8-hour token lifetime. Passwords hashed with
  bcrypt.
- `profiles` + `user_roles` tables; role assignment is a many-to-many
  relationship.
- FastAPI dependencies `get_current_user` and `require_admin` enforce
  RBAC at the router level.
- CRUD routers for users, regions, developers, estates.
- `/api/health` and `/api/health/db` endpoints; the latter reports
  connectivity and a table count (expected 19).
- Auto-seed-on-empty lifespan hook (see ADR-002).

### Data Model

Sprint 1 unlocks the following tables against the full 19-table schema
(`alembic upgrade head` creates all 19 on first deploy):

- `profiles`
- `user_roles`
- `regions`
- `developers`
- `estates`

### Frontend

- React + Vite SPA with shadcn/ui and Tailwind CSS.
- Token stored client-side; `Authorization: Bearer` injected into every
  API request.
- Protected layout with sidebar navigation.
- TanStack Table–driven estates list view with server-side pagination and
  filtering.

## Seeded Data

On first deploy into an empty database, the application seeds the
following (all passwords `Test1234!`):

| Email | Roles |
|---|---|
| admin@hbg.test | admin, pricing |
| pricing@hbg.test | pricing |
| sales1@hbg.test | sales, requester |
| sales2@hbg.test | sales, requester |
| requester@hbg.test | requester |

Plus a baseline of regions, developers, and estates sufficient to
exercise the UI and the list/filter endpoints.

## Known Limitations

- **No password reset UI.** Admins must delete and recreate a user to
  change a password in Sprint 1.
- **No email verification.** The `email_verified` column exists but is
  always `true` for seeded users.
- **No 2FA / MFA.**
- **No account lockout** on repeated failed logins.
- **No frontend production deploy yet.** The SPA is served out of the
  Railway API service; a dedicated static hosting target is planned.
- **Auto-seed is unconditional on empty DBs** — this must be gated before
  a production cutover (see ADR-002, follow-up action).
- **Session revocation is not supported** — a stolen token remains valid
  until `exp`.

## Breaking Changes

None — this is the first release.

## Contributors

Delivered by Claude Code agents:

- **Plan agent** — sprint scoping, acceptance criteria, sequencing.
- **Backend Implementation agent** — FastAPI routers, services, schemas,
  auth, tests.
- **Frontend Implementation agent** — React SPA, login flow, CRUD pages.

## Links

- **Repository:** https://github.com/JeremyBree/house-and-land-packager
- **Deployed PoC:** https://house-and-land-packager-production.up.railway.app
- **OpenAPI docs:**
  https://house-and-land-packager-production.up.railway.app/docs
- **API reference:** `docs/api/sprint-1-endpoints.md`
- **Deploy runbook:** `docs/operations/runbooks/sprint-1-deploy-and-verify.md`
- **Admin quickstart:** `docs/user-guide/sprint-1-admin-quickstart.md`

## Sprint 2 Preview

Sprint 2 will build on the estate foundation:

- **Estate stages** — define stages under each estate.
- **Stage lots** — per-lot data entry and list views.
- **Status lifecycle** — Available, Unavailable, Hold, Deposit Taken,
  Sold, with history tracking.
- Beginning of the Land Search Interface (LSI) across all active lots.

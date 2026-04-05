# Runbook: Deploy and Verify Sprint 1

This runbook covers deploying Sprint 1 of the House and Land Packager to
Railway and verifying that authentication, RBAC, and the core entity CRUD
endpoints are operational.

## Prerequisites

- Railway project linked to the GitHub repository
  `JeremyBree/house-and-land-packager`.
- PostgreSQL plugin attached to the Railway service. `DATABASE_URL` is
  injected automatically.
- The following environment variables set on the Railway service:
  - `JWT_SECRET` — strong random string (rotating invalidates all tokens).
  - `CORS_ORIGINS` — comma-separated allowed origins (e.g.
    `https://house-and-land-packager-production.up.railway.app`).
- `railway` CLI installed locally for ad-hoc logs and redeploys.

## Deploy Steps

1. Ensure your feature branch is merged to `main`. Railway auto-deploys on
   push to `main`:
   ```bash
   git checkout main
   git pull origin main
   git merge feature/sprint-1
   git push origin main
   ```
2. Watch the Railway build in the dashboard or via CLI:
   ```bash
   railway logs
   ```
3. On startup the service will:
   - Run `Base.metadata.create_all` (tables created if missing).
   - Check `profiles` row count.
   - If zero, run `seed_dev` (emits `Dev seed complete` in logs).
4. Confirm the service reports `Uvicorn running on 0.0.0.0:$PORT` in the
   deploy logs.

## Verification Checklist

Run these against the production URL
`https://house-and-land-packager-production.up.railway.app`.

### 1. API health

```bash
curl -i https://house-and-land-packager-production.up.railway.app/api/health
```
Expect `HTTP/1.1 200 OK` and body `{"status":"healthy","version":"0.1.0"}`.

### 2. Database health

```bash
curl https://house-and-land-packager-production.up.railway.app/api/health/db
```
Expect `{"status":"connected","tables":19}`.

### 3. Admin login

```bash
TOKEN=$(curl -s -X POST https://house-and-land-packager-production.up.railway.app/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@hbg.test&password=Test1234!" \
  | python -c "import sys, json; print(json.load(sys.stdin)['access_token'])")
echo "$TOKEN"
```
A non-empty JWT is returned.

### 4. Authenticated /me

```bash
curl -i https://house-and-land-packager-production.up.railway.app/api/auth/me \
  -H "Authorization: Bearer $TOKEN"
```
Expect `200 OK`, `roles` contains `"admin"` and `"pricing"`.

### 5. RBAC enforcement

```bash
SALES_TOKEN=$(curl -s -X POST https://house-and-land-packager-production.up.railway.app/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=sales1@hbg.test&password=Test1234!" \
  | python -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

curl -i https://house-and-land-packager-production.up.railway.app/api/users \
  -H "Authorization: Bearer $SALES_TOKEN"
```
Expect `403 Forbidden` with `code: insufficient_permissions` — the sales
user is blocked from the admin-only users endpoint.

### 6. Seeded data

```bash
curl https://house-and-land-packager-production.up.railway.app/api/regions \
  -H "Authorization: Bearer $TOKEN"

curl https://house-and-land-packager-production.up.railway.app/api/developers \
  -H "Authorization: Bearer $TOKEN"

curl "https://house-and-land-packager-production.up.railway.app/api/estates?size=5" \
  -H "Authorization: Bearer $TOKEN"
```
Each call returns seeded rows. Estates returns a paginated response with
`total > 0`.

### 7. Seeded user credentials

All seeded passwords are `Test1234!`.

| Email | Roles |
|---|---|
| admin@hbg.test | admin, pricing |
| pricing@hbg.test | pricing |
| sales1@hbg.test | sales, requester |
| sales2@hbg.test | sales, requester |
| requester@hbg.test | requester |

## Rollback Procedure

If a deployment introduces a regression:

1. Identify the last known-good commit on `main`:
   ```bash
   git log --oneline -20
   ```
2. Revert the offending commit(s) — create a new commit, do **not**
   force-push:
   ```bash
   git revert <bad-sha>
   git push origin main
   ```
3. Railway auto-deploys the revert commit.
4. Re-run the verification checklist above.
5. If a revert is insufficient (for example, a destructive migration),
   restore the Railway PostgreSQL plugin from its latest backup via the
   Railway dashboard before redeploying.

## Known Issues / Troubleshooting

- **"Database is empty, running dev seed..." appears unexpectedly** — the
  `profiles` table was truncated. Login with seeded credentials should
  work, but any hand-created users are gone. Restore the DB from backup.
- **401 on /api/auth/login with correct credentials** — check that
  `JWT_SECRET` has not been rotated mid-session. Clients need to log in
  again after any rotation.
- **CORS errors in the browser** — ensure the calling origin is present in
  the `CORS_ORIGINS` env var (comma-separated, no spaces).
- **`tables=19` mismatch on /api/health/db** — Alembic or
  `create_all` did not complete. Check Railway deploy logs for a migration
  traceback.
- **sales user receives 200 from /api/users** — RBAC dependency is
  misconfigured. The `users` router must have
  `dependencies=[Depends(require_admin)]` at the router level.

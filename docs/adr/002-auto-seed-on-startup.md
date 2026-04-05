# ADR-002: Auto-Seed Dev Data on Empty Database

- **Status:** Accepted (PoC-only; see follow-up action)
- **Date:** 2026-04-05
- **Related:** ADR-001 (JWT auth), ADR-016 (Railway for PoC deployment)

## Context

The House and Land Packager is deployed as a single Railway service with a
PostgreSQL plugin. First-time Railway deploys currently go through a
manual workflow:

1. `alembic upgrade head` creates the 19 tables.
2. An operator SSHes into the service (or runs a one-off job) to execute
   `python -m hlp.seeds.dev_seed`.
3. Only after seeding can anyone log in.

This friction is hostile to the PoC's goal of "clone, deploy, show".
Reviewers should be able to visit the Railway URL and log in immediately
with documented test credentials.

On the other hand, if this behaviour survives into production, a wiped or
fresh-environment deploy could silently create a set of known-password
admin accounts — a serious security risk.

## Decision

In the FastAPI `lifespan` startup hook, after creating tables:

- Count rows in `profiles`.
- If the count is **zero**, run `seed_dev(session)`, which inserts the four
  seeded users, baseline regions, developers, and estates.
- If the count is non-zero, skip seeding and log the existing profile count.

Seeding is therefore **idempotent on an empty database** and **no-op on a
populated database**.

## Consequences

### Positive

- **Zero-friction first deploy**: push to `main`, wait for Railway, log in.
- **Idempotent**: redeploys never duplicate or mutate existing data.
- Demo / review environments can be reset by dropping the database, without
  operator intervention.

### Negative

- **Production risk**: an accidental production database wipe followed by a
  restart would re-create known-password admin accounts. The seeded
  passwords (`Test1234!`) are documented publicly in the repository.
- Behaviour is implicit — a developer inspecting logs has to know to look
  for "Database is empty, running dev seed" to understand why data
  appeared.
- Couples application startup to data concerns, which normally belong in a
  migration or one-off job.

### Follow-Up Action (Required Before Production Migration)

Before the production (Azure) cutover, add a `SEED_ON_STARTUP` environment
flag (default `false`) and gate the seed block on it:

```python
if settings.seed_on_startup and profile_count == 0:
    seed_dev(session)
```

Staging and production environments must ship with `SEED_ON_STARTUP=false`.
PoC Railway environments may keep it `true`. This ADR should be superseded
when that change lands.

# Sprint 1 Acceptance Criteria — Traceability Matrix

This matrix links each Sprint 1 acceptance criterion to the tests that
verify it and the method used to confirm the behaviour. Test IDs follow
the pattern `<layer>: <module>::<test>` where `layer` is one of `UNIT`,
`INTEGRATION`, or `E2E`.

| AC # | Acceptance Criterion | Test IDs | Verification Method |
|---|---|---|---|
| AC-01 | Unauthenticated user accessing any protected page is redirected to `/login` | E2E: `test_auth_flow.py::test_unauth_redirects_to_login` | Playwright + manual browser check |
| AC-02 | JWT issued by `/api/auth/login` contains `sub`, `email`, `roles`, and `exp` claims and expires after 8 hours | UNIT: `test_security.py::test_token_contains_expected_claims`; UNIT: `test_security.py::test_token_expiry_is_480_minutes` | pytest |
| AC-03 | `/api/auth/login` returns 401 with `code: authentication_failed` for invalid credentials | INTEGRATION: `test_auth_router.py::test_login_invalid_password`; INTEGRATION: `test_auth_router.py::test_login_unknown_email` | pytest |
| AC-04 | `/api/auth/me` returns the caller's profile and roles | INTEGRATION: `test_auth_router.py::test_me_returns_current_user` | pytest |
| AC-05 | Bcrypt password hashes verify successfully and are never returned in API responses | UNIT: `test_security.py::test_password_hash_and_verify`; INTEGRATION: `test_users_router.py::test_user_read_has_no_password_field` | pytest |
| AC-06 | All `/api/users` endpoints require the `admin` role (non-admins receive 403) | INTEGRATION: `test_users_router.py::test_sales_user_forbidden`; INTEGRATION: `test_users_router.py::test_admin_can_list_users` | pytest |
| AC-07 | Admin can create a user with one or more roles, and at least one role is required | INTEGRATION: `test_users_router.py::test_create_user_with_roles`; INTEGRATION: `test_users_router.py::test_create_user_requires_roles` | pytest |
| AC-08 | Admin can update user name and job title via PATCH (email/password immutable) | INTEGRATION: `test_users_router.py::test_patch_user_updates_name` | pytest |
| AC-09 | Admin can replace a user's roles via PUT `/api/users/{id}/roles` | INTEGRATION: `test_users_router.py::test_put_user_roles_replaces_set` | pytest |
| AC-10 | Admin can delete a user and that user can no longer authenticate | INTEGRATION: `test_users_router.py::test_delete_user_then_login_fails` | pytest |
| AC-11 | Admin CRUD works end-to-end for regions | INTEGRATION: `test_regions_router.py::test_region_crud` | pytest |
| AC-12 | Admin CRUD works end-to-end for developers | INTEGRATION: `test_developers_router.py::test_developer_crud` | pytest |
| AC-13 | Admin can create, list, filter, update, and soft-delete estates; soft delete sets `active = false` | INTEGRATION: `test_estates_router.py::test_estate_crud`; INTEGRATION: `test_estates_router.py::test_delete_sets_active_false`; INTEGRATION: `test_estates_router.py::test_list_filters_by_developer_region_active` | pytest |
| AC-14 | On first startup with an empty `profiles` table, dev seed data is inserted automatically; subsequent startups skip seeding | INTEGRATION: `test_lifespan.py::test_seed_runs_when_empty`; INTEGRATION: `test_lifespan.py::test_seed_skipped_when_populated` | pytest |
| AC-15 | `/api/health` returns 200 and `/api/health/db` reports `tables=19` against the deployed database | E2E: `test_health.py::test_health_ok`; E2E: `test_health.py::test_health_db_reports_19_tables` | pytest + manual curl against Railway |

## Execution

Run the full Sprint 1 test set:

```bash
pytest tests/unit/test_security.py \
       tests/integration/test_auth_router.py \
       tests/integration/test_users_router.py \
       tests/integration/test_regions_router.py \
       tests/integration/test_developers_router.py \
       tests/integration/test_estates_router.py \
       tests/integration/test_lifespan.py \
       tests/e2e/test_auth_flow.py \
       tests/e2e/test_health.py
```

Manual verification steps for the E2E rows are captured in
`docs/operations/runbooks/sprint-1-deploy-and-verify.md`.

# ADR-001: Self-Managed JWT Authentication for PoC

- **Status:** Accepted
- **Date:** 2026-04-05
- **Related:** ADR-017 (Readme.md), ADR-016 (Railway for PoC deployment)

## Context

The House and Land Packager PoC needs authenticated access for four distinct user
roles (admin, pricing, sales, requester). For a PoC running on Railway, we
evaluated three broad options:

1. **Third-party managed auth** (Auth0, Clerk, Supabase Auth, AWS Cognito).
2. **Self-managed JWT** with bcrypt-hashed passwords and a local `user_roles`
   table.
3. **Enterprise SSO** (Microsoft Entra ID / Azure AD).

The PoC constraints that shaped the decision:

- Single Railway service, aiming for ~\$21-63/month total infrastructure cost
  (see ADR-016). Auth0's B2B tier alone starts at \$150/month.
- No external user base yet: the initial users are a handful of internal
  Hermitage/Kingsbridge staff seeded manually.
- No regulatory requirement for MFA or SSO during the PoC phase.
- We will migrate to Azure for production, at which point Entra ID is the
  natural identity provider for both SSO and MFA.
- The feature surface needed for the PoC is small: login, token issuance,
  role-based route protection, and admin-managed user CRUD.

Pulling in a third-party provider now would add vendor lock-in, a monthly
line item, and integration complexity that would all need to be unwound when
we move to Entra ID.

## Decision

Implement authentication as part of the application:

- Passwords hashed with **bcrypt** (via `passlib`).
- Access tokens issued as **JWTs** signed with HS256 using `python-jose`.
- Token lifetime: 8 hours (`jwt_expire_minutes = 480`).
- Token claims: `sub` (profile_id), `email`, `roles`, `exp`.
- User roles stored in a dedicated `user_roles` table, many-to-many against
  `profiles`. A single user may hold multiple roles.
- FastAPI dependencies (`get_current_user`, `require_admin`, etc.) enforce
  RBAC at the router level.
- User provisioning is admin-only via `/api/users` endpoints. No public
  self-service signup.

## Consequences

### Positive

- **No vendor dependency** and no per-MAU cost during the PoC.
- **Simple mental model**: one process, one database, one auth flow.
- **Easy to test**: JWTs can be minted directly in tests; no mock identity
  provider required.
- **Full control** over the claims, expiry, and role shape — which makes the
  eventual Entra ID mapping straightforward.

### Negative

- We must build (or defer) features that managed services provide out of the
  box:
  - Password reset / forgotten-password flow.
  - Email verification.
  - Two-factor authentication.
  - Account lockout / brute-force protection.
  - Audit logs for authentication events.
- HS256 shared-secret signing requires careful secret management; rotation
  requires re-issuing all live tokens.
- No built-in session revocation — a stolen token is valid until `exp`.

### Migration Path

When the PoC graduates to production on Azure, swap the current JWT issuer
for **Microsoft Entra ID** (OIDC). The target changes:

1. Replace local `/api/auth/login` with an OIDC redirect to Entra ID.
2. Validate incoming Entra-issued JWTs against the tenant's JWKS endpoint.
3. Map Entra group claims onto the existing `user_roles` values.
4. Retain the `profiles` and `user_roles` tables as the application-side
   identity record (keyed by Entra `oid`).
5. Retire the local password column; keep bcrypt hashes only for a
   break-glass service account if required.

The role-checking dependencies and the `user_roles` table remain unchanged,
so the blast radius of the migration is confined to the login route and
token validation middleware.

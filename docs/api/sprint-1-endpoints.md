# Sprint 1 API Reference

> Auto-generated OpenAPI spec is also available at
> https://house-and-land-packager-production.up.railway.app/docs

This document covers the endpoints shipped in Sprint 1: authentication, user
management, regions, developers, and estates. All endpoints are served
under the Railway base URL above.

## Conventions

- **Base URL** (PoC): `https://house-and-land-packager-production.up.railway.app`
- **Auth**: Bearer JWT in `Authorization: Bearer <token>`, obtained from
  `POST /api/auth/login`. Tokens expire after 8 hours (28800 seconds).
- **Content type**: `application/json` for all request/response bodies
  except `/api/auth/login` which uses `application/x-www-form-urlencoded`
  (OAuth2 password flow).
- **Errors** follow the shape:
  ```json
  { "detail": "human readable message", "code": "machine_code" }
  ```
  Common codes: `authentication_failed`, `insufficient_permissions`,
  `not_found`, `validation_error`, `min_roles_required`, `server_error`.
- **Pagination**: endpoints that paginate return
  `{ items, total, page, size, pages }`.

---

## Authentication

### POST /api/auth/login

Issues a JWT access token.

- **Auth**: public
- **Content-Type**: `application/x-www-form-urlencoded`
- **Request body** (form fields):
  | Field | Type | Notes |
  |---|---|---|
  | `username` | string (email) | OAuth2 password flow uses `username` |
  | `password` | string | |
- **200 Response**
  ```json
  {
    "access_token": "eyJhbGciOi...",
    "token_type": "bearer",
    "expires_in": 28800
  }
  ```
- **401 Response**: `{ "detail": "Invalid credentials", "code": "authentication_failed" }`
- **cURL**
  ```bash
  curl -X POST https://house-and-land-packager-production.up.railway.app/api/auth/login \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=admin@hbg.test&password=Test1234!"
  ```

### GET /api/auth/me

Returns the authenticated user's profile and roles.

- **Auth**: any authenticated user
- **200 Response**
  ```json
  {
    "profile_id": 1,
    "email": "admin@hbg.test",
    "first_name": "Admin",
    "last_name": "User",
    "job_title": "Administrator",
    "email_verified": true,
    "roles": ["admin", "pricing"],
    "created_at": "2026-04-05T09:00:00Z"
  }
  ```
- **401**: missing or invalid token.
- **cURL**
  ```bash
  curl https://house-and-land-packager-production.up.railway.app/api/auth/me \
    -H "Authorization: Bearer $TOKEN"
  ```

---

## Users

All `/api/users` endpoints require the `admin` role.

### GET /api/users

List users, paginated and optionally searched.

- **Query params**:
  | Name | Type | Default | Notes |
  |---|---|---|---|
  | `page` | int | 1 | `>= 1` |
  | `size` | int | 25 | `1-200` |
  | `search` | string | — | matches email, first_name, last_name |
- **200 Response**: `PaginatedResponse[UserRead]` (see `/api/auth/me` for
  the item shape).
- **cURL**
  ```bash
  curl "https://.../api/users?page=1&size=25&search=sales" \
    -H "Authorization: Bearer $TOKEN"
  ```

### POST /api/users

Create a new user with one or more roles.

- **Request body**
  ```json
  {
    "email": "newuser@hbg.test",
    "password": "Str0ngPass!",
    "first_name": "New",
    "last_name": "User",
    "job_title": "Sales Rep",
    "roles": ["sales", "requester"]
  }
  ```
  Constraints: `password` 8-128 chars; `roles` minimum length 1, must be
  drawn from `admin | pricing | sales | requester`.
- **201 Response**: `UserRead`
- **422**: validation error (e.g. duplicate email, empty roles).
- **cURL**
  ```bash
  curl -X POST https://.../api/users \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"email":"x@hbg.test","password":"Test1234!","first_name":"X","last_name":"Y","roles":["sales"]}'
  ```

### GET /api/users/{profile_id}

Fetch a single user by ID.

- **200**: `UserRead`
- **404**: user not found.

### PATCH /api/users/{profile_id}

Update mutable profile fields. Email and password are **not** editable
through this endpoint.

- **Request body** (all optional):
  ```json
  { "first_name": "Jane", "last_name": "Doe", "job_title": "Manager" }
  ```
- **200**: updated `UserRead`.
- **404**: user not found.

### PUT /api/users/{profile_id}/roles

Replace the full set of roles assigned to a user.

- **Request body**
  ```json
  { "roles": ["admin", "pricing"] }
  ```
  Minimum length 1; duplicates are de-duplicated server-side.
- **200**: updated `UserRead`.
- **400**: `min_roles_required` if the list is empty.
- **cURL**
  ```bash
  curl -X PUT https://.../api/users/5/roles \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"roles":["sales","requester"]}'
  ```

### DELETE /api/users/{profile_id}

Hard-deletes the user profile and associated role assignments.

- **204 No Content**
- **404**: user not found.

---

## Regions

### GET /api/regions

List all regions (not paginated).

- **Auth**: any authenticated user.
- **200 Response**
  ```json
  [
    { "region_id": 1, "name": "Melbourne North", "created_at": "2026-04-05T09:00:00Z" }
  ]
  ```

### POST /api/regions

- **Auth**: admin.
- **Request body**: `{ "name": "Melbourne South" }` (1-255 chars).
- **201 Response**: `RegionRead`.

### PATCH /api/regions/{region_id}

- **Auth**: admin.
- **Request body**: `{ "name": "Updated Name" }`.
- **200 Response**: `RegionRead`.
- **404**: region not found.

### DELETE /api/regions/{region_id}

- **Auth**: admin.
- **204 No Content**; **404** if region not found.

---

## Developers

### GET /api/developers

List all developers (not paginated).

- **Auth**: any authenticated user.
- **200 Response**
  ```json
  [
    {
      "developer_id": 1,
      "developer_name": "Stockland",
      "developer_website": "https://stockland.com.au",
      "contact_email": "partners@stockland.com.au",
      "notes": null,
      "created_at": "2026-04-05T09:00:00Z",
      "updated_at": "2026-04-05T09:00:00Z"
    }
  ]
  ```

### POST /api/developers

- **Auth**: admin.
- **Request body**
  ```json
  {
    "developer_name": "Stockland",
    "developer_website": "https://stockland.com.au",
    "contact_email": "partners@stockland.com.au",
    "notes": null
  }
  ```
  Only `developer_name` is required (1-255 chars).
- **201 Response**: `DeveloperRead`.

### PATCH /api/developers/{developer_id}

- **Auth**: admin.
- **Request body**: any subset of the create fields.
- **200 Response**: `DeveloperRead`.
- **404**: developer not found.

### DELETE /api/developers/{developer_id}

- **Auth**: admin.
- **204 No Content**; **404** if not found.

---

## Estates

### GET /api/estates

List estates, paginated and filterable.

- **Auth**: any authenticated user.
- **Query params**
  | Name | Type | Default | Notes |
  |---|---|---|---|
  | `page` | int | 1 | `>= 1` |
  | `size` | int | 25 | `1-200` |
  | `search` | string | — | matches estate_name, suburb |
  | `developer_id` | int | — | exact match |
  | `region_id` | int | — | exact match |
  | `active` | bool | — | `true`/`false` |
- **200 Response**: `PaginatedResponse[EstateRead]` (flat — does not embed
  developer/region).
- **cURL**
  ```bash
  curl "https://.../api/estates?developer_id=1&active=true&page=1&size=25" \
    -H "Authorization: Bearer $TOKEN"
  ```

### GET /api/estates/{estate_id}

Fetch a single estate with embedded developer and region.

- **Auth**: any authenticated user.
- **200 Response**: `EstateDetailRead` — `EstateRead` plus
  `developer: DeveloperRead` and `region: RegionRead | null`.
- **404**: estate not found.

### POST /api/estates

- **Auth**: admin.
- **Request body**
  ```json
  {
    "developer_id": 1,
    "region_id": 2,
    "estate_name": "Aurora",
    "suburb": "Epping",
    "state": "VIC",
    "postcode": "3076",
    "contact_name": "Jane Smith",
    "contact_mobile": "0400 000 000",
    "contact_email": "jane@example.com",
    "description": "Master-planned community.",
    "notes": null
  }
  ```
  Required: `developer_id`, `estate_name`.
- **201 Response**: `EstateDetailRead`.

### PATCH /api/estates/{estate_id}

- **Auth**: admin.
- **Request body**: any subset of the create fields plus `active: bool`.
- **200 Response**: `EstateDetailRead`.
- **404**: estate not found.

### DELETE /api/estates/{estate_id}

Soft-deletes the estate by setting `active = false`.

- **Auth**: admin.
- **204 No Content**.

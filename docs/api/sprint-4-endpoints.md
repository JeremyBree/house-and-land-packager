# Sprint 4 API Reference

> See also `sprint-1-endpoints.md` (auth), `sprint-2-endpoints.md`
> (stages / lots / documents), and `sprint-3-endpoints.md` (land
> search / presets). OpenAPI spec: `/docs` (Swagger UI) on the
> deployed service.

This document covers the endpoints shipped in Sprint 4: clash rules,
house packages, and conflict detection.

## Conventions

- **Base URL** (PoC): `https://house-and-land-packager-production.up.railway.app`
- **Auth**: Bearer JWT in `Authorization: Bearer <token>`.
- **Admin-only** endpoints require the `admin` role. Read endpoints
  require any authenticated user.
- **Content type**: `application/json` for requests and responses
  unless noted otherwise (flyer upload uses `multipart/form-data`).
- **Errors** follow the standard shape:
  ```json
  { "detail": "human readable message", "code": "machine_code" }
  ```
  Sprint 4 additions: `clash_rule_not_found` (404),
  `package_not_found` (404).
- **Pagination** (packages): `{ items, total, page, size, pages }`.

---

## Schemas

### `ClashRuleCreate`

| Field | Type | Constraints |
|---|---|---|
| `estate_id` | `int` | Required |
| `stage_id` | `int` | Required |
| `lot_number` | `string` | 1-50 chars |
| `cannot_match` | `list[string]` | Default `[]` |

### `ClashRuleUpdate`

| Field | Type | Constraints |
|---|---|---|
| `cannot_match` | `list[string]` | Default `[]` |

### `ClashRuleRead`

| Field | Type |
|---|---|
| `rule_id` | `int` |
| `estate_id` | `int` |
| `stage_id` | `int` |
| `lot_number` | `string` |
| `cannot_match` | `list[string]` |
| `created_at` | `datetime` |

### `ClashRuleCopyRequest`

| Field | Type |
|---|---|
| `target_estate_id` | `int` |
| `target_stage_id` | `int` |

### `PackageCreate`

| Field | Type | Constraints |
|---|---|---|
| `estate_id` | `int` | Required |
| `stage_id` | `int` | Required |
| `lot_number` | `string` | 1-50 chars |
| `design` | `string` | 1-255 chars |
| `facade` | `string` | 1-255 chars |
| `colour_scheme` | `string \| null` | Max 255 chars |
| `brand` | `string` | 1-100 chars |
| `source` | `string \| null` | Max 500 chars |
| `status` | `string \| null` | Max 50 chars |

### `PackageUpdate`

All fields optional (partial update via `PATCH`). Same types and
constraints as `PackageCreate`.

### `PackageRead`

| Field | Type |
|---|---|
| `package_id` | `int` |
| `estate_id` | `int` |
| `stage_id` | `int` |
| `lot_number` | `string` |
| `design` | `string` |
| `facade` | `string` |
| `colour_scheme` | `string \| null` |
| `brand` | `string` |
| `source` | `string \| null` |
| `status` | `string \| null` |
| `flyer_path` | `string \| null` |
| `created_at` | `datetime` |
| `updated_at` | `datetime` |

### `PackageDetailRead` (extends `PackageRead`)

| Added field | Type |
|---|---|
| `estate_name` | `string \| null` |
| `stage_name` | `string \| null` |
| `lot_id` | `int \| null` |

### `ConflictRead`

| Field | Type |
|---|---|
| `conflict_type` | `string` — `"design-facade"` or `"design-facade-colour"` |
| `severity` | `string` — `"high"` or `"critical"` |
| `package_a` | `PackageRead` |
| `package_b` | `PackageRead` |
| `rule_id` | `int` |
| `estate_id` | `int` |
| `stage_id` | `int` |
| `lot_numbers` | `list[string]` |

### `ConflictSummary`

| Field | Type |
|---|---|
| `total_conflicts` | `int` |
| `by_type` | `dict[string, int]` |
| `by_estate` | `list[ConflictEstateCount]` |

### `ConflictEstateCount`

| Field | Type |
|---|---|
| `estate_id` | `int` |
| `estate_name` | `string` |
| `count` | `int` |

---

## Clash Rules

### GET /api/estates/{estate_id}/clash-rules

List all clash rules for an estate (across all stages).

- **Auth**: any authenticated user.
- **200 Response**: `list[ClashRuleRead]`
- **404**: estate not found.
- **cURL**
  ```bash
  curl https://.../api/estates/1/clash-rules \
    -H "Authorization: Bearer $TOKEN"
  ```

### GET /api/stages/{stage_id}/clash-rules

List clash rules scoped to a specific stage.

- **Auth**: any authenticated user.
- **200 Response**: `list[ClashRuleRead]`
- **404**: stage not found.
- **cURL**
  ```bash
  curl https://.../api/stages/3/clash-rules \
    -H "Authorization: Bearer $TOKEN"
  ```

### POST /api/estates/{estate_id}/stages/{stage_id}/clash-rules

Create a clash rule. Reciprocal rules are created/updated
automatically (see ADR-006).

- **Auth**: admin only.
- **Request body**: `ClashRuleCreate` (note: `estate_id` and
  `stage_id` in the body are overridden by URL path values).
- **201 Response**: `ClashRuleRead`
- **404**: estate or stage not found.
- **Example request**
  ```json
  {
    "estate_id": 1,
    "stage_id": 3,
    "lot_number": "L101",
    "cannot_match": ["L102", "L103"]
  }
  ```
- **cURL**
  ```bash
  curl -X POST https://.../api/estates/1/stages/3/clash-rules \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"estate_id":1,"stage_id":3,"lot_number":"L101","cannot_match":["L102","L103"]}'
  ```

### GET /api/clash-rules/{rule_id}

Fetch a single clash rule by ID.

- **Auth**: any authenticated user.
- **200 Response**: `ClashRuleRead`
- **404 `clash_rule_not_found`**: rule does not exist.
- **cURL**
  ```bash
  curl https://.../api/clash-rules/5 \
    -H "Authorization: Bearer $TOKEN"
  ```

### PATCH /api/clash-rules/{rule_id}

Update the `cannot_match` list. Reciprocal rules are synced
automatically.

- **Auth**: admin only.
- **Request body**: `ClashRuleUpdate`
  ```json
  { "cannot_match": ["L102", "L104"] }
  ```
- **200 Response**: `ClashRuleRead`
- **404 `clash_rule_not_found`**: rule does not exist.
- **cURL**
  ```bash
  curl -X PATCH https://.../api/clash-rules/5 \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"cannot_match":["L102","L104"]}'
  ```

### DELETE /api/clash-rules/{rule_id}

Delete a clash rule. Does NOT remove reciprocal entries.

- **Auth**: admin only.
- **204 No Content**.
- **cURL**
  ```bash
  curl -X DELETE https://.../api/clash-rules/5 \
    -H "Authorization: Bearer $TOKEN"
  ```

### POST /api/stages/{stage_id}/clash-rules/copy

Copy all clash rules from a source stage to a target stage (bulk
upsert).

- **Auth**: admin only.
- **Request body**: `ClashRuleCopyRequest`
  ```json
  { "target_estate_id": 2, "target_stage_id": 7 }
  ```
- **200 Response**: `{ "copied": <count> }`
- **404**: source or target stage/estate not found.
- **cURL**
  ```bash
  curl -X POST https://.../api/stages/3/clash-rules/copy \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"target_estate_id":2,"target_stage_id":7}'
  ```

---

## House Packages

### GET /api/packages

List packages with optional filters and pagination.

- **Auth**: any authenticated user.
- **Query parameters**: `estate_id`, `stage_id`, `brand`, `design`,
  `facade`, `lot_number` (all optional), `page` (default 1),
  `size` (default 25, max 200).
- **200 Response**: `PaginatedResponse[PackageRead]`
  ```json
  {
    "items": [ ... PackageRead ... ],
    "total": 42,
    "page": 1,
    "size": 25,
    "pages": 2
  }
  ```
- **cURL**
  ```bash
  curl "https://.../api/packages?estate_id=1&brand=Metricon&page=1&size=25" \
    -H "Authorization: Bearer $TOKEN"
  ```

### POST /api/packages

Create a house package.

- **Auth**: admin only.
- **Request body**: `PackageCreate`
- **201 Response**: `PackageRead`
- **404**: estate or stage not found.
- **Example request**
  ```json
  {
    "estate_id": 1,
    "stage_id": 3,
    "lot_number": "L101",
    "design": "Riviera",
    "facade": "Coastal",
    "colour_scheme": "Ivory",
    "brand": "Metricon",
    "source": "builder-portal",
    "status": "active"
  }
  ```
- **cURL**
  ```bash
  curl -X POST https://.../api/packages \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"estate_id":1,"stage_id":3,"lot_number":"L101","design":"Riviera","facade":"Coastal","brand":"Metricon"}'
  ```

### GET /api/packages/{package_id}

Fetch a single package with enriched detail (estate name, stage
name, lot ID from StageLot).

- **Auth**: any authenticated user.
- **200 Response**: `PackageDetailRead`
- **404 `package_not_found`**: package does not exist.
- **cURL**
  ```bash
  curl https://.../api/packages/12 \
    -H "Authorization: Bearer $TOKEN"
  ```

### PATCH /api/packages/{package_id}

Partial update of a package.

- **Auth**: admin only.
- **Request body**: `PackageUpdate` (all fields optional).
  ```json
  { "facade": "Heritage", "colour_scheme": "Charcoal" }
  ```
- **200 Response**: `PackageRead`
- **404 `package_not_found`**: package does not exist.
- **cURL**
  ```bash
  curl -X PATCH https://.../api/packages/12 \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"facade":"Heritage","colour_scheme":"Charcoal"}'
  ```

### DELETE /api/packages/{package_id}

Delete a package.

- **Auth**: admin only.
- **204 No Content**.
- **cURL**
  ```bash
  curl -X DELETE https://.../api/packages/12 \
    -H "Authorization: Bearer $TOKEN"
  ```

### POST /api/packages/{package_id}/flyer

Upload a flyer file (PDF, image) for a package.

- **Auth**: admin only.
- **Content type**: `multipart/form-data` with a `file` field.
- **200 Response**: `PackageRead` (with `flyer_path` populated).
- **404 `package_not_found`**: package does not exist.
- **cURL**
  ```bash
  curl -X POST https://.../api/packages/12/flyer \
    -H "Authorization: Bearer $TOKEN" \
    -F "file=@flyer.pdf"
  ```

### DELETE /api/packages/{package_id}/flyer

Remove the flyer from a package.

- **Auth**: admin only.
- **204 No Content**.
- **cURL**
  ```bash
  curl -X DELETE https://.../api/packages/12/flyer \
    -H "Authorization: Bearer $TOKEN"
  ```

---

## Conflict Detection

### GET /api/conflicts

Detect and return all current conflicts (design-facade clashes
between packages on restricted lots).

- **Auth**: any authenticated user.
- **Query parameters**: `estate_id` (optional — scope to one
  estate).
- **200 Response**: `list[ConflictRead]`
- **Example response**
  ```json
  [
    {
      "conflict_type": "design-facade",
      "severity": "high",
      "package_a": { ... PackageRead ... },
      "package_b": { ... PackageRead ... },
      "rule_id": 5,
      "estate_id": 1,
      "stage_id": 3,
      "lot_numbers": ["L101", "L102"]
    }
  ]
  ```
- **cURL**
  ```bash
  curl "https://.../api/conflicts?estate_id=1" \
    -H "Authorization: Bearer $TOKEN"
  ```

### GET /api/conflicts/summary

Aggregated conflict counts for dashboard display.

- **Auth**: any authenticated user.
- **200 Response**: `ConflictSummary`
  ```json
  {
    "total_conflicts": 3,
    "by_type": {
      "design-facade": 2,
      "design-facade-colour": 1
    },
    "by_estate": [
      { "estate_id": 1, "estate_name": "Aurora Rise", "count": 2 },
      { "estate_id": 4, "estate_name": "Parkview", "count": 1 }
    ]
  }
  ```
- **cURL**
  ```bash
  curl https://.../api/conflicts/summary \
    -H "Authorization: Bearer $TOKEN"
  ```

---

## Endpoint Summary

| # | Method | Path | Auth | Router |
|---|---|---|---|---|
| 1 | GET | `/api/estates/{estate_id}/clash-rules` | user | `clash_rules.py` |
| 2 | GET | `/api/stages/{stage_id}/clash-rules` | user | `clash_rules.py` |
| 3 | POST | `/api/estates/{estate_id}/stages/{stage_id}/clash-rules` | admin | `clash_rules.py` |
| 4 | GET | `/api/clash-rules/{rule_id}` | user | `clash_rules.py` |
| 5 | PATCH | `/api/clash-rules/{rule_id}` | admin | `clash_rules.py` |
| 6 | DELETE | `/api/clash-rules/{rule_id}` | admin | `clash_rules.py` |
| 7 | POST | `/api/stages/{stage_id}/clash-rules/copy` | admin | `clash_rules.py` |
| 8 | GET | `/api/packages` | user | `packages.py` |
| 9 | POST | `/api/packages` | admin | `packages.py` |
| 10 | GET | `/api/packages/{package_id}` | user | `packages.py` |
| 11 | PATCH | `/api/packages/{package_id}` | admin | `packages.py` |
| 12 | DELETE | `/api/packages/{package_id}` | admin | `packages.py` |
| 13 | POST | `/api/packages/{package_id}/flyer` | admin | `packages.py` |
| 14 | DELETE | `/api/packages/{package_id}/flyer` | admin | `packages.py` |
| 15 | GET | `/api/conflicts` | user | `conflicts.py` |
| 16 | GET | `/api/conflicts/summary` | user | `conflicts.py` |

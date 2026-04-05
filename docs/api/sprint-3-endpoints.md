# Sprint 3 API Reference

> See also `sprint-1-endpoints.md` (auth) and `sprint-2-endpoints.md`
> (stages / lots / documents). OpenAPI spec: `/docs` (Swagger UI) on
> the deployed service.

This document covers the endpoints shipped in Sprint 3: cross-estate
lot search (Land Search Interface), CSV/XLSX export, and per-user
saved filter presets.

## Conventions

- **Base URL** (PoC): `https://house-and-land-packager-production.up.railway.app`
- **Auth**: Bearer JWT in `Authorization: Bearer <token>`. Every
  Sprint 3 endpoint requires an authenticated user. No role
  restriction — any authenticated role can search, export, and
  manage their own presets.
- **Content type**: `application/json` for requests and JSON
  responses. Exports return binary bodies with `Content-Disposition:
  attachment`.
- **Errors** follow the standard shape:
  ```json
  { "detail": "human readable message", "code": "machine_code" }
  ```
  Sprint 3 additions: `export_too_large` (413),
  `filter_preset_not_found` (404), `duplicate_preset_name` (409).
- **Pagination**: search returns
  `{ items, total, page, size, pages, filter_summary }`.

---

## Schemas

### `LotSearchFilters`

All 14 filter fields are optional; omit or set `null` to disable.
Multi-select fields are OR-within, AND-across (see AC-01).

| Field | Type | Semantics |
|---|---|---|
| `estate_ids` | `list[int] \| null` | Match any listed estate |
| `developer_ids` | `list[int] \| null` | Match any listed developer |
| `region_ids` | `list[int] \| null` | Match any listed region |
| `suburbs` | `list[str] \| null` | Match any listed estate suburb (exact) |
| `statuses` | `list[LotStatus] \| null` | Match any listed status |
| `price_min` | `decimal \| null` | `land_price >= price_min` |
| `price_max` | `decimal \| null` | `land_price <= price_max` |
| `size_min` | `decimal \| null` | `size_sqm >= size_min` |
| `size_max` | `decimal \| null` | `size_sqm <= size_max` |
| `frontage_min` | `decimal \| null` | `frontage >= frontage_min` |
| `depth_min` | `decimal \| null` | `depth >= depth_min` |
| `corner_block` | `bool \| null` | Exact match on `corner_block` |
| `title_date_from` | `date \| null` | `title_date >= title_date_from` |
| `title_date_to` | `date \| null` | `title_date <= title_date_to` |
| `exclude_null_price` | `bool` | When `true`, excludes lots with `land_price IS NULL`. Default `false`. |
| `text_search` | `str \| null` | Case-insensitive substring match across `lot_number`, `estate_name`, `estate.suburb`, `developer_name`. |

### `LotSearchRequest`

```json
{
  "filters": { ... LotSearchFilters ... },
  "page": 1,
  "size": 50,
  "sort_by": "land_price",
  "sort_desc": false
}
```

- `page` — `>= 1`, default `1`.
- `size` — `1-200`, default `50`.
- `sort_by` — one of `land_price | size_sqm | frontage | lot_number
  | estate_name | last_confirmed_date`. Invalid values fall back to
  `land_price`.
- `sort_desc` — `true` for descending, default `false`.

### `LotSearchResult` — enriched fields

Every result is a `LotRead` (see Sprint 2) with these joined fields
added:

| Added field | Source |
|---|---|
| `estate_name` | `estates.name` |
| `estate_suburb` | `estates.suburb` |
| `estate_state` | `estates.state` |
| `developer_name` | `developers.name` |
| `region_name` | `regions.name` (nullable) |
| `stage_name` | `estate_stages.name` |

### `LotSearchResponse`

```json
{
  "items": [ ... LotSearchResult ... ],
  "total": 137,
  "page": 1,
  "size": 50,
  "pages": 3,
  "filter_summary": { ... echoed non-null filters ... }
}
```

---

## Land Search

### POST /api/lots/search

Cross-estate lot search with all 14 filters, sorting, and pagination.

- **Auth**: any authenticated user.
- **Request body**: `LotSearchRequest`.
- **200 Response**: `LotSearchResponse`.
- **Example request**
  ```json
  {
    "filters": {
      "statuses": ["Available"],
      "estate_ids": [1, 3, 7],
      "price_max": "400000",
      "size_min": "400",
      "corner_block": true,
      "exclude_null_price": true,
      "text_search": "aurora"
    },
    "page": 1,
    "size": 25,
    "sort_by": "land_price",
    "sort_desc": false
  }
  ```
- **Example response**
  ```json
  {
    "items": [
      {
        "lot_id": 42,
        "stage_id": 3,
        "lot_number": "L101",
        "frontage": "12.50",
        "depth": "32.00",
        "size_sqm": "400.00",
        "corner_block": true,
        "orientation": "N",
        "land_price": "385000.00",
        "build_price": "275000.00",
        "package_price": "660000.00",
        "status": "Available",
        "title_date": "2026-02-01",
        "last_confirmed_date": "2026-04-05T09:00:00Z",
        "source": "manual",
        "estate_name": "Aurora Rise",
        "estate_suburb": "Tarneit",
        "estate_state": "VIC",
        "developer_name": "Stockland",
        "region_name": "Western Growth Corridor",
        "stage_name": "Stage 1A"
      }
    ],
    "total": 8,
    "page": 1,
    "size": 25,
    "pages": 1,
    "filter_summary": {
      "statuses": ["Available"],
      "estate_ids": [1, 3, 7],
      "price_max": "400000",
      "size_min": "400",
      "corner_block": true,
      "exclude_null_price": true,
      "text_search": "aurora"
    }
  }
  ```
- **cURL**
  ```bash
  curl -X POST https://.../api/lots/search \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"filters":{"statuses":["Available"],"price_max":"400000"},"page":1,"size":25}'
  ```

---

## Exports

Both export endpoints accept a `LotSearchFilters` body (no
pagination — the export streams the full matching result set up to
`MAX_EXPORT_ROWS = 5000`). If the match count exceeds the cap, the
export fails **before** streaming with HTTP 413.

Filename pattern: `lots_export_YYYYMMDD_HHMMSS.{csv|xlsx}` (UTC).

### POST /api/lots/export/csv

Streaming CSV export of the matching lots.

- **Auth**: any authenticated user.
- **Request body**: `LotSearchFilters`.
- **200 Response**: `text/csv; charset=utf-8` body.
  - `Content-Disposition: attachment; filename="lots_export_20260406_101530.csv"`
- **413 `export_too_large`**: match count > 5000.
- **cURL**
  ```bash
  curl -X POST https://.../api/lots/export/csv \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"statuses":["Available"]}' \
    -OJ
  ```

### POST /api/lots/export/xlsx

Formatted XLSX export (openpyxl). Headers are bold and frozen;
currency columns (`land_price`, `build_price`, `package_price`) use
a currency number format.

- **Auth**: any authenticated user.
- **Request body**: `LotSearchFilters`.
- **200 Response**:
  `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
  body.
  - `Content-Disposition: attachment; filename="lots_export_20260406_101530.xlsx"`
- **413 `export_too_large`**: match count > 5000.
- **cURL**
  ```bash
  curl -X POST https://.../api/lots/export/xlsx \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"statuses":["Available"],"estate_ids":[1]}' \
    -OJ
  ```

### 5000-row cap behaviour

Both export endpoints run a `count()` against the filters before
streaming data. If `total > 5000`, the endpoint immediately raises
`ExportTooLargeError` (413), **no partial file is produced**. The
caller must narrow the filters and retry. There is no "export only
first 5000" fallback — this is deliberate to prevent silent data
truncation.

---

## Filter Presets

Filter presets are **per-user** (see ADR-005). Every preset
endpoint is ownership-checked against the caller's `profile_id`.
Accessing another user's preset returns **404**, not 403, to avoid
leaking existence.

### GET /api/filter-presets

List the current user's presets.

- **Auth**: any authenticated user.
- **200 Response**: `list[FilterPresetRead]`
  ```json
  [
    {
      "preset_id": 12,
      "profile_id": 4,
      "name": "Budget Lots <$400k",
      "filters": {
        "statuses": ["Available"],
        "price_max": "400000",
        "exclude_null_price": true
      },
      "created_at": "2026-04-06T09:00:00Z",
      "updated_at": "2026-04-06T09:00:00Z"
    }
  ]
  ```
- **cURL**
  ```bash
  curl https://.../api/filter-presets \
    -H "Authorization: Bearer $TOKEN"
  ```

### POST /api/filter-presets

Create a new preset owned by the current user.

- **Auth**: any authenticated user.
- **Request body**
  ```json
  {
    "name": "Corner Blocks North",
    "filters": {
      "statuses": ["Available"],
      "corner_block": true,
      "region_ids": [2]
    }
  }
  ```
  `name` is 1-255 chars. `filters` is a `LotSearchFilters`.
- **201 Response**: `FilterPresetRead`.
- **409 `duplicate_preset_name`**: this user already has a preset
  with that name.
- **cURL**
  ```bash
  curl -X POST https://.../api/filter-presets \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"name":"Corner Blocks North","filters":{"corner_block":true}}'
  ```

### GET /api/filter-presets/{preset_id}

Fetch one of the current user's presets by ID.

- **Auth**: any authenticated user.
- **200**: `FilterPresetRead`.
- **404 `filter_preset_not_found`**: preset does not exist or is
  owned by another user.
- **cURL**
  ```bash
  curl https://.../api/filter-presets/12 \
    -H "Authorization: Bearer $TOKEN"
  ```

### PATCH /api/filter-presets/{preset_id}

Rename and/or replace the filters on one of the current user's
presets.

- **Auth**: any authenticated user.
- **Request body** (all optional):
  ```json
  { "name": "Budget Lots ≤$400k", "filters": { ... } }
  ```
- **200**: `FilterPresetRead`.
- **404 `filter_preset_not_found`**: preset not owned by caller.
- **409 `duplicate_preset_name`**: renaming clashes with another of
  the caller's presets.
- **cURL**
  ```bash
  curl -X PATCH https://.../api/filter-presets/12 \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"name":"Budget Lots <=$400k"}'
  ```

### DELETE /api/filter-presets/{preset_id}

Delete one of the current user's presets.

- **Auth**: any authenticated user.
- **204 No Content**.
- **404 `filter_preset_not_found`**: preset not owned by caller.
- **cURL**
  ```bash
  curl -X DELETE https://.../api/filter-presets/12 \
    -H "Authorization: Bearer $TOKEN"
  ```

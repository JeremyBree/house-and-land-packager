# Sprint 2 API Reference

> See also `sprint-1-endpoints.md` for auth endpoints.
> OpenAPI spec: `/docs` (Swagger UI) on the deployed service.

This document covers the endpoints shipped in Sprint 2: estate stages,
stage lots (CRUD, bulk, CSV upload, status lifecycle, history), estate
documents, and volume-backed file serving. All endpoints are served
under the Railway base URL below.

## Conventions

- **Base URL** (PoC): `https://house-and-land-packager-production.up.railway.app`
- **Auth**: Bearer JWT in `Authorization: Bearer <token>`, obtained
  from `POST /api/auth/login`. Tokens expire after 8 hours.
- **Content type**: `application/json` except where explicitly marked
  `multipart/form-data` (CSV and document uploads).
- **Errors** follow the shape:
  ```json
  { "detail": "human readable message", "code": "machine_code" }
  ```
  Sprint 2 additions: `stage_not_found`, `lot_not_found`,
  `document_not_found`, `unsupported_file_type`, `file_too_large`,
  `invalid_csv`.
- **Pagination**: endpoints that paginate return
  `{ items, total, page, size, pages }`.
- **Enums**:
  - `LotStatus`: `Available | Unavailable | Hold | Deposit Taken | Sold`
  - `StageStatus`: `Active | Upcoming | Completed`

---

## Stages

### GET /api/estates/{estate_id}/stages

List all stages for an estate (not paginated; stages-per-estate is
small).

- **Auth**: any authenticated user.
- **200 Response**: `list[StageRead]`
  ```json
  [
    {
      "stage_id": 1,
      "estate_id": 1,
      "name": "Stage 1A",
      "lot_count": 24,
      "status": "Active",
      "release_date": "2025-11-01",
      "created_at": "2026-04-05T09:00:00Z",
      "updated_at": "2026-04-05T09:00:00Z"
    }
  ]
  ```
- **404**: estate not found.
- **cURL**
  ```bash
  curl https://.../api/estates/1/stages \
    -H "Authorization: Bearer $TOKEN"
  ```

### POST /api/estates/{estate_id}/stages

Create a stage under an estate.

- **Auth**: admin.
- **Request body**
  ```json
  {
    "name": "Stage 2",
    "lot_count": 18,
    "status": "Upcoming",
    "release_date": "2026-06-01"
  }
  ```
  Only `name` is required (1-100 chars). `status` defaults to
  `Active`.
- **201 Response**: `StageRead`.
- **404**: estate not found.
- **cURL**
  ```bash
  curl -X POST https://.../api/estates/1/stages \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"name":"Stage 2","lot_count":18,"status":"Upcoming"}'
  ```

### GET /api/stages/{stage_id}

Fetch a stage with computed lot statistics.

- **Auth**: any authenticated user.
- **200 Response**: `StageDetailRead` — `StageRead` plus:
  ```json
  {
    "lot_count_actual": 22,
    "status_breakdown": {
      "Available": 15,
      "Hold": 2,
      "Deposit Taken": 3,
      "Sold": 2
    }
  }
  ```
  `lot_count_actual` is the count of rows in `stage_lots` for this
  stage (contrast with `lot_count`, the planned/declared size).
- **404**: stage not found.

### PATCH /api/stages/{stage_id}

Update mutable stage fields.

- **Auth**: admin.
- **Request body** (all optional):
  ```json
  { "name": "Stage 1B", "lot_count": 26, "status": "Completed", "release_date": "2025-10-15" }
  ```
- **200**: `StageRead`.
- **404**: stage not found.

### DELETE /api/stages/{stage_id}

Hard-deletes the stage. **Cascades** to all `stage_lots` and
`status_history` rows associated with the stage's lots.

- **Auth**: admin.
- **204 No Content**.
- **404**: stage not found.

---

## Lots

### GET /api/stages/{stage_id}/lots

List lots in a stage, paginated.

- **Auth**: any authenticated user.
- **Query params**
  | Name | Type | Default | Notes |
  |---|---|---|---|
  | `page` | int | 1 | `>= 1` |
  | `size` | int | 25 | `1-200` |
  | `status` | LotStatus | — | exact match |
- **200 Response**: `PaginatedResponse[LotRead]`
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
        "corner_block": false,
        "orientation": "N",
        "side_easement": "1.50",
        "rear_easement": "2.00",
        "street_name": "Aurora Blvd",
        "land_price": "385000.00",
        "build_price": "275000.00",
        "package_price": "660000.00",
        "status": "Available",
        "substation": false,
        "title_date": "2026-02-01",
        "last_confirmed_date": "2026-04-05T09:00:00Z",
        "source": "manual",
        "created_at": "2026-04-05T09:00:00Z",
        "updated_at": "2026-04-05T09:00:00Z"
      }
    ],
    "total": 22,
    "page": 1,
    "size": 25,
    "pages": 1
  }
  ```
- **404**: stage not found.
- **cURL**
  ```bash
  curl "https://.../api/stages/3/lots?status=Available&page=1&size=25" \
    -H "Authorization: Bearer $TOKEN"
  ```

### POST /api/stages/{stage_id}/lots

Create a single lot.

- **Auth**: admin.
- **Request body**
  ```json
  {
    "lot_number": "L101",
    "frontage": "12.50",
    "depth": "32.00",
    "size_sqm": "400.00",
    "corner_block": false,
    "orientation": "N",
    "side_easement": "1.50",
    "rear_easement": "2.00",
    "street_name": "Aurora Blvd",
    "land_price": "385000.00",
    "build_price": "275000.00",
    "package_price": "660000.00",
    "substation": false,
    "title_date": "2026-02-01"
  }
  ```
  Only `lot_number` is required (1-50 chars). New lots are created
  with `status = Available` and `source = manual`.
- **201 Response**: `LotRead`.
- **404**: stage not found.
- **422**: validation error (including duplicate `(stage_id, lot_number)`).

### POST /api/stages/{stage_id}/lots/bulk

Create many lots in a single JSON request. Duplicates within the
payload, and lots whose `lot_number` already exists in the target
stage, are **skipped (not errored)**.

- **Auth**: admin.
- **Request body**
  ```json
  {
    "lots": [
      { "lot_number": "L101", "frontage": "12.5", "size_sqm": "400" },
      { "lot_number": "L102", "frontage": "14.0", "size_sqm": "448" }
    ]
  }
  ```
- **200 Response**: `CsvUploadResult`
  ```json
  { "created": 2, "skipped": 0, "errors": [] }
  ```
- **404**: stage not found.
- **cURL**
  ```bash
  curl -X POST https://.../api/stages/3/lots/bulk \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"lots":[{"lot_number":"L101"},{"lot_number":"L102"}]}'
  ```

### POST /api/stages/{stage_id}/lots/upload-csv

Create lots from a CSV file. Column spec and examples are in
`docs/operations/runbooks/sprint-2-csv-upload-guide.md`.

- **Auth**: admin.
- **Content-Type**: `multipart/form-data`
- **Form fields**:
  | Field | Type | Notes |
  |---|---|---|
  | `file` | file | UTF-8 CSV; header row required |
- **200 Response**: `CsvUploadResult` (same shape as bulk endpoint).
  Parse errors from individual rows surface as an `InvalidCsvError`
  (`invalid_csv`) 400 response for the entire upload — the CSV is
  parsed all-or-nothing before any insertions occur.
- **400**: `invalid_csv` — malformed CSV, missing `lot_number`
  header, invalid boolean/decimal/date value.
- **404**: stage not found.
- **cURL**
  ```bash
  curl -X POST https://.../api/stages/3/lots/upload-csv \
    -H "Authorization: Bearer $TOKEN" \
    -F "file=@lots.csv"
  ```

### GET /api/lots/{lot_id}

Fetch a single lot.

- **Auth**: any authenticated user.
- **200**: `LotRead`.
- **404**: `lot_not_found`.

### PATCH /api/lots/{lot_id}

Update mutable lot fields. Does **not** transition status — use the
status endpoint for that.

- **Auth**: admin.
- **Request body**: any subset of the `LotCreate` fields.
- **200**: `LotRead`.
- **404**: lot not found.

### DELETE /api/lots/{lot_id}

Hard-deletes the lot and cascades to its `status_history` rows.

- **Auth**: admin.
- **204 No Content**.
- **404**: lot not found.

### POST /api/lots/{lot_id}/status

Transition a lot to a new status. Creates a `status_history` row and
updates `last_confirmed_date`. See ADR-004 for the full audit
semantics.

- **Auth**: **admin or pricing**.
- **Request body**
  ```json
  { "new_status": "Hold", "reason": "Held for agent XYZ until Friday" }
  ```
  `reason` is required (1-500 chars). Any `LotStatus` value is
  accepted, including the current status (a "refresh").
- **200**: updated `LotRead`.
- **404**: lot not found.
- **403**: caller lacks admin/pricing role.
- **cURL**
  ```bash
  curl -X POST https://.../api/lots/42/status \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"new_status":"Hold","reason":"Held for agent XYZ"}'
  ```

### GET /api/lots/{lot_id}/status-history

Return the full status history for a lot, most recent first.

- **Auth**: any authenticated user.
- **200 Response**: `list[StatusHistoryRead]`
  ```json
  [
    {
      "history_id": 87,
      "lot_id": 42,
      "previous_status": "Available",
      "new_status": "Hold",
      "changed_at": "2026-04-05T12:00:00Z",
      "triggering_agent": "manual:admin@hbg.test",
      "source_detail": "Held for agent XYZ"
    }
  ]
  ```
- **404**: lot not found.

---

## Documents

### POST /api/estates/{estate_id}/documents

Upload a document against an estate (optionally scoped to a stage
within that estate).

- **Auth**: admin.
- **Content-Type**: `multipart/form-data`
- **Query params**:
  | Name | Type | Notes |
  |---|---|---|
  | `stage_id` | int | optional; must belong to the estate |
  | `description` | string | optional |
- **Form fields**:
  | Field | Type | Notes |
  |---|---|---|
  | `file` | file | max 10 MB; PDF, DOC, DOCX, PNG, JPG, JPEG |
- **201 Response**: `DocumentRead`
  ```json
  {
    "document_id": 12,
    "estate_id": 1,
    "stage_id": null,
    "file_name": "price-list.pdf",
    "file_type": "PDF",
    "file_size": 284712,
    "description": "Developer price list Apr 2026",
    "created_at": "2026-04-05T12:00:00Z",
    "download_url": "/api/files/estate-documents/ab12...ef_price-list.pdf"
  }
  ```
- **400**: `unsupported_file_type` or `file_too_large`.
- **404**: estate (or stage if supplied) not found.
- **cURL**
  ```bash
  curl -X POST "https://.../api/estates/1/documents?description=Price+list" \
    -H "Authorization: Bearer $TOKEN" \
    -F "file=@price-list.pdf"
  ```

### GET /api/estates/{estate_id}/documents

List documents belonging to an estate.

- **Auth**: any authenticated user.
- **200 Response**: `list[DocumentRead]`.
- **404**: estate not found.

### GET /api/documents/{document_id}

Download a document. Returns the raw file bytes with
`Content-Disposition: attachment; filename="<original_name>"` and a
best-effort `Content-Type` inferred from the original filename.

- **Auth**: any authenticated user.
- **200**: binary body.
- **404**: document not found.
- **cURL**
  ```bash
  curl -OJ https://.../api/documents/12 \
    -H "Authorization: Bearer $TOKEN"
  ```

### DELETE /api/documents/{document_id}

Delete the document row and remove the underlying file from the
volume. If the file is already missing from disk, the DB row is still
deleted (the storage delete is best-effort).

- **Auth**: admin.
- **204 No Content**.
- **404**: document not found.

---

## Files

### GET /api/files/{category}/{filename}

Serve a file directly from the storage volume. Used by the
`download_url` returned on `DocumentRead` responses.

- **Auth**: any authenticated user.
- **Path params**:
  - `category` — one of `estate-documents`, `package-flyers`,
    `generated-sheets`.
  - `filename` — the stored filename as returned by
    `StorageService.save_file` (e.g.
    `ab12cd34...ef_price-list.pdf`).
- **200**: binary body with `Content-Type` inferred from the filename.
- **404**: unknown category, or file missing from disk.
- **cURL**
  ```bash
  curl -OJ https://.../api/files/estate-documents/ab12cd34ef_price-list.pdf \
    -H "Authorization: Bearer $TOKEN"
  ```

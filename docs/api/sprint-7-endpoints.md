# Sprint 7 API Endpoints

## Dashboard

### GET /api/dashboard
- **Auth**: Any authenticated user
- **Response**: `DashboardRead`
  - `total_estates` (int)
  - `total_lots` (int)
  - `total_packages` (int)
  - `active_conflicts` (int)
  - `pending_requests` (int)
  - `lot_status_breakdown` (dict: status name -> count)
  - `recent_requests` (list of last 5 pricing requests with brand, status, estate/stage names, lot count)

## Configurations (Admin only)

### GET /api/configurations
- **Auth**: Admin
- **Query params**: `type` (email_account|website|portal|pdf_folder), `enabled` (bool)
- **Response**: `list[ConfigurationRead]`

### POST /api/configurations
- **Auth**: Admin
- **Body**: `ConfigurationCreate` (config_type, label, url_or_path, credentials_ref?, run_schedule?, enabled, priority_rank, notes?, scraping_config?)
- **Response**: `ConfigurationRead` (201)

### GET /api/configurations/{id}
- **Auth**: Admin
- **Response**: `ConfigurationRead`

### PATCH /api/configurations/{id}
- **Auth**: Admin
- **Body**: `ConfigurationUpdate` (all fields optional)
- **Response**: `ConfigurationRead`

### DELETE /api/configurations/{id}
- **Auth**: Admin
- **Response**: 204 No Content

### POST /api/configurations/{id}/toggle
- **Auth**: Admin
- **Response**: `ConfigurationRead` (enabled field toggled)

### Note on credentials masking
The `credentials_ref` field is masked in all responses: if set, it appears as `"[configured]"`; if null, it remains null. The actual environment variable name is never exposed via the API.

## Ingestion Logs (Admin only)

### GET /api/ingestion-logs
- **Auth**: Admin
- **Query params**: `page` (int, default 1), `size` (int, default 25), `agent_type` (email|scraper|portal|pdf), `status` (success|partial|failed)
- **Response**: `PaginatedResponse[IngestionLogRead]`

### GET /api/ingestion-logs/{id}
- **Auth**: Admin
- **Response**: `IngestionLogRead` (includes error_detail for failed runs)

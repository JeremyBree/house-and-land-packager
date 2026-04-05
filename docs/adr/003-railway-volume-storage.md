# ADR-003: Railway Volume for File Storage

- **Status:** Accepted (PoC-only)
- **Date:** 2026-04-05
- **Related:** ADR-016 (Railway for PoC deployment), ADR-001 (JWT auth)

## Context

Sprint 2 introduces estate documents, and later sprints will add
package flyers and generated pricing sheets. Each of these is a binary
blob that must be:

- Uploaded by an admin through the API.
- Retrieved later by any authenticated user.
- Associated with a database row (`estate_documents`, and future
  `packages`, `pricing_sheets` tables) via a stored relative path.

The file-storage options considered for the PoC:

1. **Database BLOBs** — store the file bytes directly in PostgreSQL.
2. **Railway Volume** — persistent disk attached to the Railway service
   at a mount point.
3. **Azure Blob Storage** — the target for production on Azure.
4. **S3-compatible object storage** (Cloudflare R2, Backblaze B2).

Constraints:

- The PoC runs as a single Railway service (see ADR-016). A Railway
  Volume is included in the existing service plan at no extra cost.
- Document sizes are bounded (PDF/DOC/image, ≤10 MB each), so a few
  hundred files fit comfortably on a volume.
- The production target is Azure Blob Storage; we want to keep the
  migration surface small.

## Decision

Store files on a **Railway Volume** mounted at `/data/storage/`, wrapped
by a `StorageService` abstraction in
`src/hlp/shared/storage_service.py`.

Key design elements:

- Three storage **categories**, each a subdirectory of the volume:
  `estate-documents`, `package-flyers`, `generated-sheets`.
- **File naming**: `{uuid4_hex}_{sanitized_original_name}.{ext}` — the
  UUID prefix guarantees uniqueness; the sanitized original name aids
  human inspection of the volume.
- **Path escape guard**: `StorageService._resolve()` rejects absolute
  paths and any path containing `..`.
- **Size/type validation** happens in `document_service`, not in
  `StorageService`. The storage layer is deliberately content-agnostic.
- Files are served through `GET /api/files/{category}/{filename}`,
  which requires an authenticated user.

Only the `StorageService` class touches the filesystem. Routers and
services call `save_file`, `read_file`, `delete_file`,
`get_download_url`, and `get_absolute_path` exclusively.

## Consequences

### Positive

- **Zero additional infrastructure cost** — the volume is bundled with
  the Railway service plan.
- **Simple mental model** — files live on local disk, indexed by a
  relative path stored in the database row.
- **Single abstraction point** for the future Azure Blob swap.
- Deleting a document row also deletes the underlying file via
  `StorageService.delete_file`, keeping the volume in lockstep with
  the DB.

### Negative

- **Not horizontally scalable.** A Railway volume is bound to a single
  service replica; we cannot scale the API out while keeping file
  access consistent.
- **No signed URLs.** Every file fetch goes through the FastAPI
  service, consuming a request slot for what could otherwise be a CDN
  hit.
- **No CDN / edge caching.** Acceptable for PoC traffic; not
  acceptable for production.
- **No automatic backups.** Railway volumes are not snapshotted on the
  service's standard plan (see the storage runbook for the operational
  consequences).
- **Tight coupling to the Railway runtime.** The volume path, mount
  semantics, and lifecycle are Railway-specific.

### Migration Path

When the PoC moves to Azure, replace the `StorageService`
implementation with one backed by the **Azure Blob Storage SDK**
(`azure-storage-blob`):

1. Implement `AzureBlobStorageService` exposing the same methods
   (`save_file`, `read_file`, `delete_file`, `get_download_url`,
   `get_absolute_path`).
2. Return **SAS URLs** from `get_download_url` instead of
   `/api/files/...`.
3. Swap the factory in `get_storage_service()` based on a
   `STORAGE_BACKEND` env var (`volume` | `azure_blob`).
4. Run a one-off migration script that reads every file from the
   volume and uploads it under the same relative path to the target
   container.

The `file_path` column in `estate_documents` already uses a
forward-slash POSIX path, which maps directly onto an Azure Blob name —
no DB migration required.

No other application code should need to change.

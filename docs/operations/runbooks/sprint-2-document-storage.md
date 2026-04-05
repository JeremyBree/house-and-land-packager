# Runbook: Estate Document Storage

This runbook describes how estate documents are stored on the Railway
volume, how to inspect and clean the volume, and the backup risks
operators need to understand.

See also **ADR-003** for the storage design rationale.

## Volume Layout

The Railway service mounts a persistent volume at
`/data/storage/`. All uploaded files live underneath it, organised by
**category**:

```
/data/storage/
├── estate-documents/      # Sprint 2: documents attached to estates/stages
├── package-flyers/        # (future sprint) PDF flyers per package
└── generated-sheets/      # (future sprint) generated pricing sheets
```

Only the `estate-documents` category is written to in Sprint 2; the
other two directories are created on first use.

### File Naming

Each stored file is named:

```
{uuid4_hex}_{sanitized_original_name}.{ext}
```

For example, a user uploading `Price List (April 2026).pdf` produces:

```
/data/storage/estate-documents/c4f1e2ab9d7e4f0b8d12cafe34567890_Price_List__April_2026_.pdf
```

- The 32-char UUID prefix guarantees uniqueness (no collisions even
  across estates / stages).
- The sanitized suffix preserves the original filename for human
  inspection. Unsafe characters are replaced with underscores; the
  extension is lowercased.
- The **`file_path`** column in `estate_documents` stores a
  forward-slash relative path like
  `estate-documents/c4f1e2ab..._Price_List__April_2026_.pdf`. The
  `StorageService` resolves this against the volume base path.

### The `file_name` vs `file_path` Distinction

- `file_name` (`estate_documents.file_name`) — the **original
  human-readable** filename at upload time. This is what the
  `Content-Disposition` header advertises on download.
- `file_path` — the **stored relative path** on disk, including the
  UUID prefix. Operators should always reference this when locating
  the physical file.

## Allowed File Types and Size Limit

Enforced by `document_service` before anything is written to disk:

| Type | Extension(s) | Max size |
|---|---|---|
| PDF | `.pdf` | 10 MB |
| Word (legacy) | `.doc` | 10 MB |
| Word (Open XML) | `.docx` | 10 MB |
| PNG image | `.png` | 10 MB |
| JPEG image | `.jpg`, `.jpeg` | 10 MB |

Rejected uploads return a 400 response with code
`unsupported_file_type` or `file_too_large`.

## Backups — KNOWN RISK

> **Railway volumes are NOT automatically backed up** on the
> service's standard plan used for this PoC. If the volume is lost
> (service deletion, volume corruption, plan change), all uploaded
> documents are permanently lost.

This is a deliberate PoC-only trade-off — the PostgreSQL plugin is
backed up, but the volume is not. Operators need to be aware:

- Treat the volume as **ephemeral** for recovery-planning purposes.
- If a specific document is business-critical, keep a copy in
  SharePoint / OneDrive until the production migration lands.
- Document uploads during the PoC phase may be re-requested from the
  originating developer.

**Production mitigation**: the production environment will use Azure
Blob Storage with soft-delete and geo-redundant replication enabled
(see ADR-003 migration path).

## Inspecting the Volume

Connect to the Railway service shell:

```bash
railway shell
```

### List all stored documents

```bash
ls -lah /data/storage/estate-documents/
```

### Count by category

```bash
for cat in estate-documents package-flyers generated-sheets; do
  count=$(ls /data/storage/$cat 2>/dev/null | wc -l)
  echo "$cat: $count"
done
```

### Total size on disk

```bash
du -sh /data/storage/
```

## Cleaning Orphaned Files

An **orphaned** file is one present on the volume but with no
matching `estate_documents.file_path` row in the database. These can
accumulate if a delete ever fails after the DB row is removed, or if
a file is manually placed on the volume.

### Find orphans

Run inside the Railway shell (requires `psql` and `DATABASE_URL`):

```bash
# 1. Export DB-known paths to a temp file
psql "$DATABASE_URL" -At -c \
  "SELECT file_path FROM estate_documents" \
  > /tmp/db_paths.txt

# 2. List actual volume paths
find /data/storage -type f -printf "%P\n" > /tmp/disk_paths.txt

# 3. Diff — files on disk that are NOT in DB
sort /tmp/db_paths.txt > /tmp/db_paths.sorted
sort /tmp/disk_paths.txt > /tmp/disk_paths.sorted
comm -23 /tmp/disk_paths.sorted /tmp/db_paths.sorted
```

The output is the list of orphaned relative paths.

### Delete orphans (manual, review first)

```bash
# Dry run — REVIEW the output before removing anything
comm -23 /tmp/disk_paths.sorted /tmp/db_paths.sorted \
  | while read rel; do echo "WOULD DELETE: /data/storage/$rel"; done

# When satisfied, delete
comm -23 /tmp/disk_paths.sorted /tmp/db_paths.sorted \
  | while read rel; do rm -v "/data/storage/$rel"; done
```

Never run these commands automatically. Always review the candidate
list before removing anything — a false positive is a permanent data
loss.

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `404 not_found` on `/api/files/...` | File missing from disk but DB row exists | Orphaned DB row; either re-upload or delete the `estate_documents` row. |
| Upload returns `file_too_large` | File exceeds 10 MB | Compress the PDF or resize the image. |
| Upload returns `unsupported_file_type` | Extension / MIME type not in allow-list | Convert to PDF. |
| Volume full (writes fail) | Quota exhausted | `du -sh /data/storage/` to locate heavy dirs; contact Railway support to raise the quota; or delete unused documents. |
| Download returns `application/octet-stream` unexpectedly | `mimetypes.guess_type` couldn't infer from the original filename | Cosmetic only — the file is still served correctly. Client should use `Content-Disposition` filename. |

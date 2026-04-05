# Sprint 2 Acceptance Criteria — Traceability Matrix

This matrix links each Sprint 2 acceptance criterion to the tests
that verify it and the method used to confirm the behaviour. Test IDs
follow the pattern `<layer>: <module>::<test>` where `layer` is one
of `UNIT`, `INTEGRATION`, or `E2E`.

| AC # | Acceptance Criterion | Test IDs | Verification Method |
|---|---|---|---|
| AC-01 | Admin can create, list, update, and delete stages under an estate | INTEGRATION: `test_stages_router.py::test_stage_crud_under_estate`; INTEGRATION: `test_stages_router.py::test_list_stages_for_estate` | pytest |
| AC-02 | Non-admin users cannot create, update, or delete stages (403) | INTEGRATION: `test_stages_router.py::test_sales_cannot_create_stage`; INTEGRATION: `test_stages_router.py::test_pricing_cannot_delete_stage` | pytest |
| AC-03 | Deleting a stage cascades to all its lots and their status history | INTEGRATION: `test_stages_router.py::test_delete_stage_cascades_lots`; INTEGRATION: `test_stages_router.py::test_delete_stage_cascades_status_history` | pytest |
| AC-04 | `GET /api/stages/{id}` returns `lot_count_actual` and a `status_breakdown` dict keyed by LotStatus | INTEGRATION: `test_stages_router.py::test_stage_detail_includes_stats` | pytest |
| AC-05 | Admin can create a lot singly, and `(stage_id, lot_number)` uniqueness is enforced (422 on duplicate) | INTEGRATION: `test_lots_router.py::test_create_lot`; INTEGRATION: `test_lots_router.py::test_duplicate_lot_number_rejected` | pytest |
| AC-06 | Bulk create endpoint creates new lots and skips (not errors) duplicates within the payload and against existing rows | INTEGRATION: `test_lots_router.py::test_bulk_create_skips_duplicates`; UNIT: `test_lot_service.py::test_bulk_create_skips_within_payload` | pytest |
| AC-07 | CSV upload parses a valid UTF-8 CSV with header row, creates all valid rows, and rejects the whole file on any parse error | UNIT: `test_lot_service.py::test_parse_csv_upload_happy_path`; UNIT: `test_lot_service.py::test_parse_csv_rejects_invalid_boolean`; INTEGRATION: `test_lots_router.py::test_upload_csv_endpoint` | pytest |
| AC-08 | CSV upload accepts booleans as yes/no/true/false/1/0/y/n (case-insensitive) and dates as YYYY-MM-DD | UNIT: `test_lot_service.py::test_parse_bool_accepts_all_forms`; UNIT: `test_lot_service.py::test_parse_date_iso_only` | pytest |
| AC-09 | Status transitions are permitted for admin and pricing roles only; sales and requester receive 403 | INTEGRATION: `test_lots_router.py::test_admin_can_transition_status`; INTEGRATION: `test_lots_router.py::test_pricing_can_transition_status`; INTEGRATION: `test_lots_router.py::test_sales_cannot_transition_status` | pytest |
| AC-10 | Every status transition (including refreshes where new==current) creates a `status_history` row with `triggering_agent="manual:{email}"` | INTEGRATION: `test_lots_router.py::test_transition_creates_history`; UNIT: `test_lot_service.py::test_refresh_transition_still_writes_history`; UNIT: `test_lot_service.py::test_triggering_agent_format` | pytest |
| AC-11 | A status transition updates the lot's `last_confirmed_date` to the transition timestamp | UNIT: `test_lot_service.py::test_transition_updates_last_confirmed_date`; INTEGRATION: `test_lots_router.py::test_transition_updates_last_confirmed` | pytest |
| AC-12 | Document upload validates file type (PDF/DOC/DOCX/PNG/JPG/JPEG) and size (≤10 MB), rejecting others with 400 | INTEGRATION: `test_documents_router.py::test_upload_rejects_exe`; INTEGRATION: `test_documents_router.py::test_upload_rejects_oversize`; UNIT: `test_document_service.py::test_resolve_file_type_unsupported` | pytest |
| AC-13 | Uploaded documents can be downloaded with the correct `Content-Type` (or `application/octet-stream` fallback) and `Content-Disposition` filename | INTEGRATION: `test_documents_router.py::test_download_returns_correct_content_type`; INTEGRATION: `test_files_router.py::test_serve_file_sets_content_disposition` | pytest |
| AC-14 | Deleting a document removes both the DB row and the underlying file from the volume | INTEGRATION: `test_documents_router.py::test_delete_document_removes_file`; UNIT: `test_storage_service.py::test_delete_file` | pytest |
| AC-15 | Seed data contains ~25 stages and ~250 lots with VIC-realistic dimensions and prices, distributed across lot statuses | INTEGRATION: `test_dev_seed.py::test_seed_creates_expected_stage_count`; INTEGRATION: `test_dev_seed.py::test_seed_creates_expected_lot_count`; INTEGRATION: `test_dev_seed.py::test_seed_lot_status_distribution` | pytest |

## Execution

Run the full Sprint 2 test set:

```bash
pytest tests/unit/test_lot_service.py \
       tests/unit/test_document_service.py \
       tests/unit/test_storage_service.py \
       tests/integration/test_stages_router.py \
       tests/integration/test_lots_router.py \
       tests/integration/test_documents_router.py \
       tests/integration/test_files_router.py \
       tests/integration/test_dev_seed.py
```

Manual verification (document upload, CSV upload via the UI) is
covered in `docs/user-guide/sprint-2-managing-lots.md` and the CSV
and document-storage runbooks.

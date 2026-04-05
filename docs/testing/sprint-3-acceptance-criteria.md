# Sprint 3 Acceptance Criteria — Traceability Matrix

This matrix links each Sprint 3 acceptance criterion to the tests
that verify it and the method used to confirm the behaviour. Test
IDs follow the pattern `<layer>: <module>::<test>` where `layer` is
one of `UNIT`, `INTEGRATION`, or `E2E`.

| AC # | Acceptance Criterion | Test IDs | Verification Method |
|---|---|---|---|
| AC-01 | All 14 LSI filters correctly scope the result set: AND across distinct fields, OR within multi-select arrays | INTEGRATION: `test_lot_search_router.py::test_all_fourteen_filters_narrow_results`; UNIT: `test_lot_search_repository.py::test_and_across_fields_or_within_lists` | pytest |
| AC-02 | `text_search` matches `lot_number`, `estate_name`, `estate.suburb`, and `developer_name` case-insensitively | UNIT: `test_lot_search_repository.py::test_text_search_matches_all_four_columns`; INTEGRATION: `test_lot_search_router.py::test_text_search_case_insensitive` | pytest |
| AC-03 | Pagination validates page `>= 1` and caps size at 200; defaults are `page=1`, `size=50` | INTEGRATION: `test_lot_search_router.py::test_pagination_defaults`; INTEGRATION: `test_lot_search_router.py::test_size_over_200_rejected` | pytest |
| AC-04 | Search is sortable on `land_price`, `size_sqm`, `frontage`, `lot_number`, `estate_name`, `last_confirmed_date`; invalid `sort_by` falls back to `land_price` | UNIT: `test_lot_search_schema.py::test_normalized_sort_falls_back`; INTEGRATION: `test_lot_search_router.py::test_sort_by_each_allowed_field` | pytest |
| AC-05 | When `exclude_null_price=true`, lots with `land_price IS NULL` are excluded from results | UNIT: `test_lot_search_repository.py::test_exclude_null_price_flag`; INTEGRATION: `test_lot_search_router.py::test_exclude_null_price_end_to_end` | pytest |
| AC-06 | Every `LotSearchResult` includes the joined `estate_name`, `developer_name`, `region_name`, `stage_name`, `estate_suburb`, `estate_state` fields | UNIT: `test_lot_search_repository.py::test_search_joins_return_enriched_columns`; INTEGRATION: `test_lot_search_router.py::test_result_includes_enriched_fields` | pytest |
| AC-07 | CSV export returns a UTF-8 body with the correct header row and one row per matching lot, with proper CSV escaping | UNIT: `test_export_service.py::test_csv_header_row`; UNIT: `test_export_service.py::test_csv_row_encoding_escapes_commas`; INTEGRATION: `test_lot_search_router.py::test_export_csv_endpoint` | pytest |
| AC-08 | XLSX export produces a valid openpyxl workbook with bold frozen header row and currency number format on `land_price` / `build_price` / `package_price` | UNIT: `test_export_service.py::test_xlsx_header_is_bold_and_frozen`; UNIT: `test_export_service.py::test_xlsx_currency_columns_formatted`; INTEGRATION: `test_lot_search_router.py::test_export_xlsx_endpoint` | pytest |
| AC-09 | Exports that would match more than 5000 rows fail with HTTP 413 `export_too_large` before any file is streamed | INTEGRATION: `test_lot_search_router.py::test_export_over_cap_returns_413`; UNIT: `test_lot_search_router.py::test_collect_export_rows_raises_when_over_cap` | pytest |
| AC-10 | Filter presets are per-user: GET/PATCH/DELETE against another user's preset ID returns 404 `filter_preset_not_found` | INTEGRATION: `test_filter_presets_router.py::test_cannot_read_other_users_preset`; INTEGRATION: `test_filter_presets_router.py::test_cannot_update_other_users_preset`; INTEGRATION: `test_filter_presets_router.py::test_cannot_delete_other_users_preset` | pytest |
| AC-11 | Creating or renaming a preset to a name already used by the same user returns 409 `duplicate_preset_name` | INTEGRATION: `test_filter_presets_router.py::test_create_duplicate_name_rejected`; INTEGRATION: `test_filter_presets_router.py::test_rename_clashing_name_rejected` | pytest |
| AC-12 | Any authenticated user (admin, pricing, sales, requester) can search, export, and manage their own presets — no role restriction | INTEGRATION: `test_lot_search_router.py::test_all_roles_can_search`; INTEGRATION: `test_lot_search_router.py::test_all_roles_can_export`; INTEGRATION: `test_filter_presets_router.py::test_all_roles_can_manage_own_presets` | pytest |

## Execution

Run the full Sprint 3 test set:

```bash
pytest tests/unit/test_lot_search_repository.py \
       tests/unit/test_lot_search_schema.py \
       tests/unit/test_export_service.py \
       tests/integration/test_lot_search_router.py \
       tests/integration/test_filter_presets_router.py
```

Manual verification (opening Land Search, saving and loading
presets, downloading CSV/XLSX exports) is covered in
`docs/user-guide/sprint-3-land-search-guide.md`.

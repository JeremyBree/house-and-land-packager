# Sprint 4 Acceptance Criteria — Traceability Matrix

This matrix links each Sprint 4 acceptance criterion to the tests
that verify it and the method used to confirm the behaviour. Test
IDs follow the pattern `<layer>: <module>::<test>` where `layer` is
one of `UNIT`, `INTEGRATION`, or `E2E`.

| AC # | Acceptance Criterion | Test IDs | Verification Method |
|---|---|---|---|
| AC-01 | Creating a clash rule for lot A with `cannot_match: [B]` automatically creates a reciprocal rule for lot B with `cannot_match: [A]` | UNIT: `test_clash_service.py::test_create_rule_creates_reciprocal`; INTEGRATION: `test_clash_rules_router.py::test_bidirectional_reciprocal_created` | pytest |
| AC-02 | Clash rules are scoped to `(estate_id, stage_id)` — rules for estate 1 / stage 3 do not appear when querying estate 2 or stage 4 | INTEGRATION: `test_clash_rules_router.py::test_rules_scoped_to_estate_and_stage`; UNIT: `test_clash_rule_repository.py::test_list_by_stage_filters_correctly` | pytest |
| AC-03 | Copying clash rules from stage A to stage B upserts all rules into the target stage; existing rules in the target are merged, not duplicated | UNIT: `test_clash_service.py::test_copy_upserts_without_duplicates`; INTEGRATION: `test_clash_rules_router.py::test_copy_clash_rules_endpoint` | pytest |
| AC-04 | House package CRUD: create returns 201 with all fields populated; get returns `PackageDetailRead` with `estate_name`, `stage_name`, and `lot_id`; patch updates only supplied fields; delete returns 204 | INTEGRATION: `test_packages_router.py::test_create_package_201`; INTEGRATION: `test_packages_router.py::test_get_package_detail_enriched`; INTEGRATION: `test_packages_router.py::test_patch_partial_update`; INTEGRATION: `test_packages_router.py::test_delete_package_204` | pytest |
| AC-05 | Package list supports filtering by `estate_id`, `stage_id`, `brand`, `design`, `facade`, and `lot_number`; results are paginated with default `page=1`, `size=25`, max size 200 | INTEGRATION: `test_packages_router.py::test_list_filters_and_pagination`; INTEGRATION: `test_packages_router.py::test_size_over_200_rejected` | pytest |
| AC-06 | Flyer upload via `POST /api/packages/{id}/flyer` stores the file and sets `flyer_path` on the package; flyer delete via `DELETE /api/packages/{id}/flyer` clears `flyer_path` and returns 204 | INTEGRATION: `test_packages_router.py::test_upload_flyer`; INTEGRATION: `test_packages_router.py::test_delete_flyer` | pytest |
| AC-07 | `GET /api/packages/{id}` returns `lot_id` by joining `StageLot` on `(stage_id, lot_number)` — confirming the package is linked to the correct lot record | INTEGRATION: `test_packages_router.py::test_get_package_lot_id_sync` | pytest |
| AC-08 | Conflict detection identifies `design-facade` (high severity) conflicts when two packages on clashing lots share the same design + facade (case-insensitive) | UNIT: `test_conflict_service.py::test_design_facade_conflict_detected`; INTEGRATION: `test_conflicts_router.py::test_high_severity_conflict` | pytest |
| AC-09 | Conflict detection identifies `design-facade-colour` (critical severity) conflicts when design + facade + colour scheme all match (case-insensitive, non-empty colour) | UNIT: `test_conflict_service.py::test_design_facade_colour_critical`; INTEGRATION: `test_conflicts_router.py::test_critical_severity_conflict` | pytest |
| AC-10 | Conflicts are deduplicated by sorted `(package_a_id, package_b_id)` pair — bidirectional rules do not produce duplicate conflict entries | UNIT: `test_conflict_service.py::test_dedup_by_sorted_pair`; INTEGRATION: `test_conflicts_router.py::test_no_duplicate_conflicts` | pytest |
| AC-11 | `GET /api/conflicts/summary` returns `total_conflicts`, `by_type` counts, and `by_estate` with estate names sorted by count descending | INTEGRATION: `test_conflicts_router.py::test_conflict_summary_shape` | pytest |
| AC-12 | Clash rule create, update, delete, copy, and package create, update, delete, flyer upload/delete all require the `admin` role; non-admin users receive 403 | INTEGRATION: `test_clash_rules_router.py::test_non_admin_rejected`; INTEGRATION: `test_packages_router.py::test_non_admin_rejected` | pytest |

## Execution

Run the full Sprint 4 test set:

```bash
pytest tests/unit/test_clash_service.py \
       tests/unit/test_clash_rule_repository.py \
       tests/unit/test_conflict_service.py \
       tests/integration/test_clash_rules_router.py \
       tests/integration/test_packages_router.py \
       tests/integration/test_conflicts_router.py
```

Manual verification (creating clash rules, adding packages, viewing
conflicts) is covered in
`docs/user-guide/sprint-4-clash-rules-and-packages.md`.

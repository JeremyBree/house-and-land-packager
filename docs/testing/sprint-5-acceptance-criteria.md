# Sprint 5 Acceptance Criteria

| AC # | Criterion | Test IDs | Method |
|---|---|---|---|
| AC-01 | Admin can upload .xlsx/.xlsm template per brand | INT: test_pricing_templates_api::test_admin_uploads_template | pytest |
| AC-02 | Data validations extracted from uploaded template | INT: test_pricing_templates_api::test_get_validations | pytest |
| AC-03 | Cell mappings can be updated per template | INT: test_pricing_templates_api::test_update_mappings | pytest |
| AC-04 | Non-admin cannot upload templates (403) | INT: test_pricing_templates_api::test_non_admin_upload_403 | pytest |
| AC-05 | Rule categories can be created per brand | INT: test_pricing_rules_api::test_create_category | pytest |
| AC-06 | Global rules created with all fields including condition | INT: test_pricing_rules_api::test_create_global_rule | pytest |
| AC-07 | Stage rules scoped to estate+stage | INT: test_pricing_rules_api::test_create_stage_rule | pytest |
| AC-08 | Rule duplication creates independent copy | INT: test_pricing_rules_api::test_duplicate_global_rule | pytest |
| AC-09 | Condition DSL: corner_block evaluates correctly | UNIT: test_pricing_rule_service::test_corner_block | pytest |
| AC-10 | Condition DSL: null condition always included | UNIT: test_pricing_rule_service::test_no_condition | pytest |
| AC-11 | Condition DSL: unknown condition excluded (fail-safe) | UNIT: test_pricing_rule_service::test_unknown | pytest |
| AC-12 | Seeded data: categories, global rules, stage rules present | Startup seed verification | Manual |

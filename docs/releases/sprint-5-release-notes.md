# Sprint 5 Release Notes

**Date:** 2026-04-06  
**Goal:** Pricing templates and rules engine — the last prerequisite for Sprint 6's pricing request workflow.

## What's New

- **Pricing Template Upload** — Admin uploads brand-specific Excel templates (.xlsx/.xlsm) for Hermitage Homes and Kingsbridge Homes
- **Data Validation Extraction** — System automatically extracts dropdown options from uploaded templates (house_type, facade_type, bdm, wholesale_group, garage_side)
- **Cell Mappings** — Configure header mappings (field → cell), column mappings (lot field → column), sheet name, and data start row
- **Global Pricing Rules** — Brand-wide rules with conditional logic (e.g., "$2,500 Corner Block Surcharge" applied only when corner_block=true)
- **Stage Pricing Rules** — Estate+stage-specific rule overrides
- **Rule Categories** — Logical grouping (Commission, Site Costs, Extras)
- **Rule Duplication** — Quick-copy a rule for editing as a new entry
- **Condition DSL** — 8 condition types: corner_block, building_crossover, is_kdrb, is_10_90_deal, developer_land_referrals, custom_house_design, house_type:{value}, wholesale_group:{value}

## Technical Additions

- 21 new API endpoints (templates, categories, global rules, stage rules)
- TemplateService with openpyxl data validation extraction
- PricingRuleService with condition evaluation engine
- Seeded: 4 categories, 7 global rules, 2 stage rules

## Known Limitations

- No visual cell mapper yet (mappings configured via JSON payload)
- Template upload replaces file but keeps existing mappings (must manually clear if template structure changed)
- Condition DSL is simple string-based (no AND/OR/NOT)

## What's Next

**Sprint 6 — Pricing Request Workflow (Core Business Feature):** Sales submits multi-lot pricing request → system validates clash rules → generates pre-filled Excel from brand template with pricing rules applied → pricing team uploads completed sheet → packages imported automatically.

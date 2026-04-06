# Sprint 5 API Reference — Pricing Templates & Rules

> Auto-generated OpenAPI spec: https://house-and-land-packager-production.up.railway.app/docs

## Pricing Templates

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | /api/pricing-templates | admin | List all templates |
| GET | /api/pricing-templates/{brand} | any | Get template by brand slug ("hermitage" or "kingsbridge") |
| POST | /api/pricing-templates/{brand}/upload | admin | Upload .xlsx/.xlsm template (multipart) |
| PATCH | /api/pricing-templates/{template_id}/mappings | admin | Update cell mappings |
| GET | /api/pricing-templates/{brand}/validations | any | Get extracted data validations |

## Pricing Rule Categories

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | /api/pricing-rule-categories?brand= | admin | List categories for brand |
| POST | /api/pricing-rule-categories | admin | Create category |
| PATCH | /api/pricing-rule-categories/{id} | admin | Update category |
| DELETE | /api/pricing-rule-categories/{id} | admin | Delete category |

## Global Pricing Rules

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | /api/pricing-rules/global?brand= | admin | List global rules for brand |
| POST | /api/pricing-rules/global | admin | Create global rule |
| GET | /api/pricing-rules/global/{id} | admin | Get rule by ID |
| PATCH | /api/pricing-rules/global/{id} | admin | Update rule |
| DELETE | /api/pricing-rules/global/{id} | admin | Delete rule |
| POST | /api/pricing-rules/global/{id}/duplicate | admin | Duplicate rule as new |

## Stage Pricing Rules

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | /api/pricing-rules/stage?estate_id=&stage_id= | admin | List stage rules |
| POST | /api/pricing-rules/stage | admin | Create stage rule |
| GET | /api/pricing-rules/stage/{id} | admin | Get rule by ID |
| PATCH | /api/pricing-rules/stage/{id} | admin | Update rule |
| DELETE | /api/pricing-rules/stage/{id} | admin | Delete rule |
| POST | /api/pricing-rules/stage/{id}/duplicate | admin | Duplicate rule as new |

## Condition DSL

Rules with a `condition` field are evaluated against a RequestContext at submission time:

| Condition | Evaluates True When |
|---|---|
| `null` (no condition) | Always applies |
| `corner_block` | Any selected lot is a corner block |
| `building_crossover` | "Building crossover" toggle is on |
| `is_kdrb` | "Is KDRB" toggle is on |
| `is_10_90_deal` | "10/90 deal" toggle is on |
| `developer_land_referrals` | "Developer Land Referrals" toggle is on |
| `custom_house_design` | Any lot has custom house design toggled |
| `house_type:{value}` | Value appears in the list of selected house types |
| `wholesale_group:{value}` | Selected wholesale group matches value |

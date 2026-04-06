# ADR-008: Pricing Rule Condition DSL

**Status:** Accepted  
**Date:** 2026-04-06  
**Sprint:** 5

## Context

Pricing rules need conditional evaluation at submission time. Rules may apply only when certain conditions are true (e.g., corner block surcharge, crossover cost). We need a simple, extensible way to express conditions without requiring code changes to add new condition types.

## Decision

Use a string-based condition DSL stored in the rule's `condition` field:

- **Boolean flags:** `corner_block`, `building_crossover`, `is_kdrb`, `is_10_90_deal`, `developer_land_referrals`, `custom_house_design` — evaluate to true/false against RequestContext
- **Keyed values:** `house_type:{value}` checks if value is in context's house_types array; `wholesale_group:{value}` checks equality
- **No condition (null):** Rule always applies
- **Unknown condition:** Rule excluded (fail-safe)

## Consequences

**Positive:**
- Simple to store and query (single string column)
- New boolean conditions can be added without schema changes
- Keyed conditions support value-specific matching
- Fail-safe on unknown conditions prevents applying incorrect rules

**Negative:**
- No complex logic (no AND/OR/NOT combinations)
- Condition values are case-sensitive for keyed types
- No validation that condition string is well-formed at entry time

**How to apply:** When building Sprint 6's spreadsheet generator, call `pricing_rule_service.evaluate_rules(rules, context)` to filter applicable rules before injecting into the template.

# Pricing Configuration Guide

## Overview

The pricing system uses brand-specific Excel templates with configurable cell mappings and conditional pricing rules. When a pricing request is submitted (Sprint 6), the system generates a pre-filled spreadsheet with all applicable rules injected.

## Pricing Templates

### Uploading a Template

1. Navigate to **Admin → Pricing Templates**
2. Select the brand (Hermitage Homes or Kingsbridge Homes)
3. Click **Upload Template** and select your .xlsx or .xlsm file
4. The system extracts data validations (dropdown options) automatically

### Cell Mappings

Configure how data maps into the template:

- **Sheet Name** — which sheet to populate (e.g., "Pricing")
- **Data Start Row** — the row where lot data begins
- **Header Mappings** — map fields (estate_name, suburb, developer, etc.) to specific cells
- **Column Mappings** — map lot fields (lot_number, house_type, facade_type, etc.) to columns

### Data Validations

After upload, the system displays extracted dropdown options:
- house_type, facade_type, bdm, wholesale_group, garage_side
- These populate dropdown fields in the pricing request form

## Pricing Rules

### Rule Types

- **Global Rules** — Apply to ALL estates/stages for a given brand
- **Stage Rules** — Apply only to a specific estate and stage combination (overrides)

### Rule Properties

| Property | Description |
|---|---|
| Item Name | Display name (e.g., "Site Costs", "Corner Block Surcharge") |
| Cost | Dollar amount |
| Condition | When this rule applies (see below) |
| Cell Row/Col | Where the item name is written in the template |
| Cost Cell Row/Col | Where the cost value is written |
| Category | Logical grouping (Commission, Site Costs, etc.) |

### Conditions

Rules can be conditional — applied only when certain criteria are met:

| Condition | Applied When |
|---|---|
| *(none)* | Always |
| Corner Block | Any selected lot is a corner block |
| Building Crossover | "Building the crossover" is toggled on |
| KDRB | "Is KDRB" is toggled on |
| 10/90 Deal | "10/90 deal" is toggled on |
| Developer Land Referrals | Toggle is on |
| Custom House Design | Any lot has custom design toggled |

### Managing Rules

- **Create** — click "+ Add Rule", fill in all fields
- **Edit** — click the pencil icon on any rule row
- **Duplicate** — click the copy icon to create a new rule pre-filled with the source rule's data
- **Delete** — click the trash icon (with confirmation)
- **Categories** — create categories to group rules logically; assign rules to categories

## What's Next

Sprint 6 will use these templates and rules to generate pricing request spreadsheets automatically.

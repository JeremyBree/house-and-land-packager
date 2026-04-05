# House and Land Packager — Project Setup

> **Version:** 3.0  
> **Date:** 5 April 2026  
> **Status:** Draft — For Team Review  
> **Source Documents:** LAAS_Combined_BRD.docx (13 Sections + Addendum A: Land Search Interface), PackagingRequirements_Document.docx (House & Land Package Pricing & Clash Management)  
> **Development Team Model:** Claude Code Agents (agentic AI-assisted development)

---

## 1. Project Overview

### 1.1 Purpose

House and Land Packager is a **web-based platform** that combines two complementary capabilities:

1. **Land Data Aggregation** — Automated collection, normalisation, and centralisation of residential land lot availability and pricing data from multiple external sources (developer websites, portals, emails, PDFs) via autonomous AI agents.
2. **House & Land Package Management** — A pricing request workflow, clash rule enforcement engine, Excel template generation system, and package management tool for two home-building brands: **Hermitage Homes** and **Kingsbridge Homes**.

The aggregation layer replaces manual consultant research. The packaging layer enables sales teams to submit pricing requests, administrators to configure pricing templates and rules, and pricing teams to fulfil requests — with automatic clash detection to prevent identical house designs on adjacent lots.

### 1.2 Business Problem

| Current State | Target State |
|---|---|
| Consultants manually search developer websites for lot data | AI agents autonomously scrape and ingest lot data on schedule |
| Portal logins done individually, data copied into spreadsheets | Portal access agent logs in, extracts data, writes to central DB |
| Email updates from developers manually parsed and transcribed | Email reader agent extracts structured lot data from email body and attachments |
| PDF price lists downloaded and manually entered | PDF pickup agent detects, OCRs, and extracts lot data automatically |
| No single source of truth — data scattered across spreadsheets, emails, bookmarks | Centralised relational database with full provenance tracking |
| Lot availability unknown until manually checked | Lot status lifecycle automatically managed — absent lots marked Unavailable within one refresh cycle |
| Compiling a land package takes hours of manual research | Consultant searches a filtered interface and finds matching lots in seconds |
| Pricing requests handled via ad-hoc emails and manual spreadsheet creation | Structured pricing request workflow with auto-generated pre-filled Excel spreadsheets |
| Clash detection done manually or not at all | Automated clash rule enforcement prevents identical designs on adjacent lots at submission time |
| Each brand's pricing template manually populated | Brand-specific templates with cell-level mapping and conditional pricing rule injection |
| No visibility into conflicting packages across estates | Dashboard and conflicts page surface all active clashes in real time |

### 1.3 Success Criteria

| Metric | Target |
|---|---|
| Manual search time per package | Reduced by >80% within 3 months of go-live |
| Data freshness | All sources checked at least once every 24 hours |
| Lot status accuracy | Unavailable lots marked within 1 data refresh cycle |
| Estate coverage | All configured estates reflected in database within ingestion window |
| Agent uptime | 99% scheduled execution success rate |
| Pricing request turnaround | Spreadsheet generated within seconds of submission |
| Clash detection accuracy | 100% of clash rule violations caught at submission time |
| Package conflict visibility | All active conflicts surfaced on dashboard in real time |

### 1.4 Scope Boundaries

**In Scope:**

- Automated email ingestion and parsing (email-based developer updates)
- Web scraping of estate and developer websites (JS-rendered pages)
- Automated portal login and data extraction (with securely stored credentials)
- Automated PDF pickup, OCR, parsing, and data extraction
- Centralised relational database storing estate, developer, lot, and package data
- Agentic AI orchestration layer to coordinate all data collection tasks
- Configuration management UI for adding/editing sources without code changes
- Lot status lifecycle management (Available, Unavailable, Hold, Deposit Taken, Sold)
- Data provenance tracking — recording the source of each record
- Land Search Interface (LSI) — internal read-only web UI for consultants
- Multi-lot pricing request submission with pre-filled Excel spreadsheet generation
- Clash rule enforcement at submission time (within-request and against existing packages)
- Stage-scoped and global pricing rule configuration with conditional logic
- Brand-specific Excel template management with cell-level mapping (Hermitage Homes, Kingsbridge Homes)
- Automated conflict detection across imported packages
- Role-based access control (Admin, Pricing, Sales, Requester)
- In-app notification system for completed pricing requests
- Document and flyer management per estate and stage
- Package import from Excel files and browsing/management

**Out of Scope:**

- CRM integration or direct quoting beyond pricing sheets (Phase 2 consideration)
- Customer-facing or client portal interfaces
- Financial or legal due diligence on land data
- Management of land developer relationships
- Map view, saved searches, comparison mode, price history charts (future enhancements)

---

## 2. Functional Breakdown

The system comprises **three major subsystems**: the Ingestion Pipeline (agents + orchestrator + database), the Land Search Interface (LSI), and the House & Land Packaging System. All share the same database.

### 2.1 Ingestion Pipeline

#### Agent 1 — Email Reader Agent (BRD §5.1)

| Capability | Description | Priority |
|---|---|---|
| Email account connection | Connect to configured email accounts via IMAP/OAuth2 or Microsoft Graph API | Must Have |
| Email filtering | Filter emails by sender domain, subject keywords, or configured rules | Must Have |
| Body extraction | Extract structured lot data from HTML and plain text email bodies | Must Have |
| Attachment processing | Parse lot data from attached PDF, XLSX, CSV, HTML files | Must Have |
| AI-assisted extraction | Use LLM prompt pipeline for semi-structured/unstructured content | Must Have |
| Provenance tagging | Tag each record with source='email', sender address, received timestamp | Must Have |
| Deduplication | Maintain processed message ID log to avoid reprocessing | Must Have |

#### Agent 2 — Web Scraper Agent (BRD §5.2)

| Capability | Description | Priority |
|---|---|---|
| Configurable target URLs | Accept target URL list from configuration layer | Must Have |
| JS rendering | Navigate and render JavaScript-heavy pages via headless browser (Playwright) | Must Have |
| Flexible selectors | Identify lot listings using CSS selectors, XPath, or AI-assisted DOM parsing | Must Have |
| Field extraction | Extract all required lot fields from listing pages or summary tables | Must Have |
| Pagination handling | Follow pagination and sub-page navigation as configured | Must Have |
| Provenance tagging | Tag each record with source='website' and source URL | Must Have |
| Ethical scraping | Respect robots.txt, implement configurable crawl delays | Must Have |
| CAPTCHA handling | Detect CAPTCHA gracefully, flag for manual review (no bypass) | Should Have |

#### Agent 3 — Portal Access Agent (BRD §5.3)

| Capability | Description | Priority |
|---|---|---|
| Secure credential retrieval | Retrieve portal credentials from encrypted secrets vault | Must Have |
| Automated login | Automate browser-based login flow for each configured portal | Must Have |
| Post-login navigation | Navigate to pricing/availability pages after authentication | Must Have |
| Data extraction | Extract lot data from portal pages, tables, or downloadable assets | Must Have |
| Session management | Handle session timeouts, re-authenticate as needed | Must Have |
| MFA flagging | Flag portals requiring MFA for manual intervention | Should Have |
| Provenance tagging | Tag each record with source='portal' and portal identifier | Must Have |

#### Agent 4 — PDF Pickup Agent (BRD §5.4)

| Capability | Description | Priority |
|---|---|---|
| Folder monitoring | Monitor configured folder paths (local, network, cloud storage) for new PDFs | Must Have |
| Auto-detection | Automatically detect and process newly added PDF files | Must Have |
| Text extraction + OCR | Use PDF text extraction and/or OCR for scanned documents | Must Have |
| AI-assisted field extraction | Handle varied PDF layouts via LLM extraction pipeline | Must Have |
| Provenance tagging | Tag each record with source='pdf', filename, detection timestamp | Must Have |
| Archive processing | Move processed PDFs to a designated archive folder | Should Have |

#### Agent 5 — Orchestrator (BRD §5.5)

| Capability | Description | Priority |
|---|---|---|
| Scheduling | Schedule each agent per configurable run intervals (cron expressions) | Must Have |
| Task queue management | Manage agent task queues, handle retries on failure (3x exponential backoff) | Must Have |
| Unified logging | Capture agent runs, records processed, errors, data changes in IngestionLog | Must Have |
| Manual trigger | Support manual trigger of any agent via admin interface | Must Have |
| Data normalisation | AI-assisted normalisation to reconcile field naming/format differences across sources | Must Have |
| Conflict resolution | Resolve same-lot conflicts using configurable source priority ranking | Must Have |
| Alerting | Emit alerts (email/notification) on agent failure or data anomalies | Should Have |
| Dry-run mode | All agents support dry-run that reports what would be ingested without DB writes | Must Have |

#### Lot Status Lifecycle Engine (BRD §5.6)

This is the critical business logic that runs after every ingestion cycle:

| Rule | Logic |
|---|---|
| **Rule 1 — Active Feed** | Lot present in latest ingestion → status = Available (or source-provided status) |
| **Rule 2 — Absent from Feed** | Lot previously present but missing from latest run for that source → status = Unavailable; Last Confirmed Date preserved |
| **Rule 3 — Multi-Source** | Lot tracked across multiple sources → only mark Unavailable when absent from ALL sources, unless a single authoritative source declares it unavailable |
| **Rule 4 — Status Values** | Permitted: Available, Unavailable, Hold, Deposit Taken, Sold. Source-provided status takes precedence. If no status but lot is present → Available assumed |

### 2.2 Configuration Management (BRD §5.7, §9)

The system must provide a configuration interface (admin web UI and/or structured config file) for:

| Source Type | Configurable Fields |
|---|---|
| **Website** | Label, target URL, estate mapping, scraping strategy (CSS/XPath/AI), pagination rules, run interval, rate limiting, enabled toggle |
| **Portal** | Label, URL, login URL, credential reference (secrets vault pointer), login form selectors, post-login navigation path, session handling rules, run interval, enabled toggle |
| **Email** | Account identifier, inbox, filter rules (sender domain, subject keywords, date range), attachment types, estate mapping rules, run interval, enabled toggle |
| **PDF Folder** | Folder path, file naming patterns (glob/regex), estate mapping rules, archive folder path, run interval, enabled toggle |
| **General** | Source priority rankings for conflict resolution, estate-to-developer name mapping, enable/disable individual sources without deletion |

### 2.3 Land Search Interface — LSI (Addendum A)

A **read-only** internal web interface for consultants to search and filter the centralised lot database.

#### Filter Panel (Addendum A §3.1)

| Filter | Input Type | Behaviour |
|---|---|---|
| Estate | Multi-select searchable dropdown | OR query across selected estates |
| Region / Suburb | Multi-select dropdown or tag input | Populated from Estate suburb/state fields |
| Price Range | Dual-handle range slider + manual inputs | Inclusive min/max. Null prices excluded by default, toggle to show |
| Lot Size (m²) | Min/max numeric inputs | Either bound optional |
| Frontage (m) | Min numeric input | Lots >= specified value |
| Depth (m) | Min numeric input | Lots >= specified value |
| Status | Checkbox group | Default: Available only. Sold/Unavailable hidden, accessible via 'Show all' |
| Title Date | Date range picker | Optional window filter |

#### Results Table (Addendum A §3.2)

- Default sort: price ascending. All column headers sortable.
- Pagination: 25/50/100 per page. Total count displayed prominently.
- Minimum columns: Estate, Stage, Lot Number, Price, Frontage, Depth, Size (m²), Title Date, Status, Last Confirmed Date.
- Status as colour-coded badges: green (Available), amber (Hold), orange (Deposit Taken), red (Sold), grey (Unavailable).
- Stale data warning: rows with Last Confirmed Date > 7 days visually flagged.
- Responsive: horizontal scroll on smaller screens, sticky Estate column.

#### Additional LSI Requirements

| Feature | Spec |
|---|---|
| Lot Detail | Click row → slide-over panel with all fields including source, developer, ingestion timestamp, source link |
| Export | Download current filtered result set (all pages) as CSV. Optional XLSX. Filename timestamped. |
| Free-text Search | Partial-match across estate name, lot number, suburb, developer name. Debounced 300ms. |
| Filter Persistence | Filters survive page refresh (session storage). URL query string reflects filter state for bookmarking/sharing. |
| Layout | Desktop: two-panel (280-320px filter left, flexible results right). Mobile (<1024px): filter drawer/bottom sheet. |
| Performance | Filter results within 1 second at 50,000 lots. LCP under 2.5 seconds. Export of 5,000 records within 10 seconds. |

#### LSI API Endpoints (Addendum A §5.2)

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/lots` | GET | Paginated, filtered, sorted lot list |
| `/api/lots/:id` | GET | Full lot detail by ID |
| `/api/estates` | GET | All estates (filter dropdown population) |
| `/api/regions` | GET | Distinct suburb/state values (region filter) |
| `/api/lots/export` | GET | Full filtered result as CSV/XLSX |

### 2.4 House & Land Packaging System

This subsystem manages the full lifecycle of house and land packages for Hermitage Homes and Kingsbridge Homes.

#### 2.4.1 User Roles & Authentication

The system uses email/password authentication with role-based access control.

| Role | Access Level |
|---|---|
| **Admin** | Full system access: user management, template configuration, pricing rules, all requests |
| **Pricing** | View and fulfil all pricing requests; upload completed pricing sheets |
| **Sales** | Submit pricing requests and view own submissions |
| **Requester** | Base role for submitting pricing requests |

Authentication features: email/password login, password reset via email, email verification required, session persistence across browser refreshes. User roles stored in a dedicated `user_roles` table (not on profiles) to prevent privilege escalation.

#### 2.4.2 Dashboard

| Feature | Description |
|---|---|
| Total Packages | Count of all imported house & land packages |
| Active Conflicts | Count of detected clashes (red if > 0, green if none) |
| Estates Tracked | Total number of estates in the system |
| Clash Rules | Total number of defined clash rules |
| Active Conflicts Display | Lists all detected conflicts with source files for both conflicting packages |
| Estate Summary | Per-estate breakdown showing package count and conflict count |

#### 2.4.3 Estates, Stages & Lots

**Estates** are the top-level organisational unit, grouped optionally by region. Each estate contains stages, which contain lots.

| Entity | Properties |
|---|---|
| **Region** | Name (e.g., Western Melbourne, Northern Melbourne). Estates optionally belong to a region. |
| **Estate** | Name, Suburb, Developer, Region (optional), Contact Name/Mobile/Email, Description |
| **Stage** | Name, Lot Count, Status (Active/Upcoming/Completed), Release Date |
| **Lot** | Lot Number (unique per stage), Frontage, Depth, Size (m²), Corner Block, Orientation, Side Easement, Rear Easement, Street Name, Land Price, Build Price, Package Price, Design, Facade, Brand, Status, Substation |

Lot operations include individual creation/editing via inline table, bulk creation by lot number range, bulk import from pricing sheets (parsed from uploaded Excel files), inline editing with auto-save, and individual deletion.

#### 2.4.4 Pricing Request Workflow

The pricing request workflow is the core business process. Sales team members submit requests which generate pre-filled Excel spreadsheets. The pricing team then fulfils these requests by uploading completed sheets.

**Submission Form:**

| Section | Fields |
|---|---|
| Estate Selection | Searchable combobox with suburb display; selecting resets stage/lot |
| General Details | Has land titled? (toggle + titling date if no), Is KDRB? (toggle), Is 10/90 deal? (toggle), Developer Land Referrals? (toggle), Building crossover? (toggle), Side/Rear Easement (auto-populated read-only), Shared crossovers? (toggle) |
| Brand Selection | Hermitage Homes or Kingsbridge Homes — determines template and visible fields |
| Hermitage-Specific | BDM (required), Wholesale Group (required), Garage Side (required per lot), Orientation (read-only from lot) |
| Kingsbridge-Specific | Custom House Design (toggle per lot) |
| Stage & Lots | Stage selector, multiple lot entries (each a separate card), per-lot: Lot No, House Type, Facade Type, plus brand-specific fields. Auto-populated read-only: Street Name, Lot Width/Depth/Size, Corner Block, Orientation, Land Price |

**Validated inputs:** When the pricing template has extracted data validations (e.g., for house_type, facade_type, bdm, wholesale_group, garage_side), fields render as dropdowns with valid options. When no validations exist, fields render as free-text inputs.

**Clash Rule Validation at Submission:**

| Pass | Logic |
|---|---|
| **Pass 1 — Within request** | For each pair of lots in the submission, check if a clash rule exists between them. If a rule exists AND both lots share the same design and facade → request BLOCKED |
| **Pass 2 — Against existing packages** | For each lot, find all lots restricted by clash rules. Fetch existing packages on those restricted lots. If any existing package has the same design and facade → request BLOCKED |

Error messages include lot numbers, design name, and facade name.

**Spreadsheet Generation:**

On successful submission, a pre-filled Excel spreadsheet (.xlsm) is generated from the brand-specific template:
- Template downloaded from cloud storage (falls back to local file)
- Header-level data injected into mapped cells (estate name, suburb, developer, contact info, toggles)
- Lot-level data injected into data rows starting at the configured `data_start_row`
- Pricing rules (global and stage-specific) with cell mappings applied conditionally
- Conditional rules evaluate context: corner_block, building_crossover, is_kdrb, custom_house_design, house_types, wholesale_group
- Generated file uploaded to cloud storage and linked to the pricing request record

**Request Lifecycle:**

Status flow: **Pending → In Progress → Completed**

- Download Generated Sheet: auto-generated pre-filled spreadsheet
- Upload Completed: pricing team uploads finalised pricing sheet
- On upload completion: packages extracted from Excel and imported into database
- Resubmit: reopens a completed request as a new draft with all fields pre-populated
- Delete: users delete own requests; admins/pricing can delete any
- Notification sent to original requester on completion

#### 2.4.5 Clash Rules & Conflict Detection

**Clash Rules:**

- Define which lots cannot have the same design and facade combination
- Scoped to a specific estate AND stage — not universal
- Each rule specifies: Estate, Stage, Lot Number, and an array of lots it cannot clash with
- Rules are bidirectional in enforcement (if A cannot clash with B, then B cannot clash with A)
- Unique constraint on (estate_id, stage_id, lot_number)
- Rules managed per-stage within estate detail view
- Stage-level clash rules can be copied to another stage (same estate or different estate) with upsert to avoid duplicates

**Conflict Detection:**

- Runs client-side against fetched package and clash rule data
- For each clash rule, find packages on the rule's lot and packages on restricted lots
- If any two packages share the same design AND facade (case-insensitive) → conflict flagged
- Conflict types: design-facade (high severity), design-facade-colour (if colour scheme also matches)
- Conflicts displayed on Dashboard and dedicated Conflicts page
- Deduplication by sorted package ID pair

#### 2.4.6 Pricing Templates & Cell Mappings

Each brand has a pricing template — an Excel file (.xlsx/.xlsm) that serves as the base for generated pricing sheets.

| Feature | Description |
|---|---|
| Template Management | Separate template per brand. Upload .xlsx/.xlsm/.xls. Prompt to keep or clear mappings when replacing. Stored in cloud storage under `pricing-templates/` |
| Header Mappings | Map field names (estate_name, suburb, developer, etc.) to specific cells (row, col) |
| Column Mappings | Map lot data fields to columns in the data area |
| Data Start Row | The row number where lot data begins |
| Sheet Name | Which sheet in the workbook to target |
| Cell Mapper | Visual Excel cell mapper component for interactive cell selection |
| Data Validations | Extracted from uploaded template; populate dropdown options in pricing request form (house_type, facade_type, bdm, wholesale_group, garage_side) |

#### 2.4.7 Pricing Rules Engine

Pricing rules define costs and conditions applied to generated spreadsheets.

| Property | Description |
|---|---|
| Item Name | e.g., "Site Costs", "Corner Block Surcharge" |
| Cost | Dollar amount |
| Condition | Optional — e.g., "corner_block", "building_crossover" |
| Condition Value | Optional |
| Cell Row / Col | Where the item name is written in the template |
| Cost Cell Row / Col | Where the cost value is written |
| Category | Optional grouping via pricing_rule_categories |
| Sort Order | Display ordering |

**Rule Types:**
- **Global Pricing Rules** — Apply to ALL estates/stages for a given brand
- **Stage Pricing Rules** — Apply only to a specific estate and stage combination

**Conditional Rule Evaluation** builds a `RequestContext` from form data at submission time:
- `corner_block`: true if any selected lot is a corner block
- `building_crossover`: from the toggle
- `is_kdrb`: from the toggle
- `is_10_90_deal`: from the toggle
- `developer_land_referrals`: from the toggle
- `custom_house_design`: true if any lot has this toggled
- `house_types`: array of all house type values
- `wholesale_group`: selected wholesale group string

Rules with a condition are only applied if the condition evaluates to true against this context.

**Rule Operations:** Create, edit (inline), delete, duplicate (copies data into creation form for quick editing as new rule). Cell references displayed as Excel-style (e.g., C5, AB12). Admin can create categories per brand to group rules logically.

#### 2.4.8 Package Management

Packages represent assigned house designs on specific lots — the data against which clash rules are enforced.

| Property | Description |
|---|---|
| Estate, Stage, Lot Number | Location of the package |
| Design, Facade, Colour Scheme | House configuration |
| Brand | Hermitage Homes or Kingsbridge Homes |
| Source | Filename from which it was imported |
| Status | Current package status |
| Flyer Path | Optional attached flyer document |

**Operations:** Import from Excel files (via Upload page or pricing request completion), browse all packages with searchable/filterable table, delete individual packages (clears design/facade/brand from associated stage lot), upload/delete flyer documents per package, view packages filtered by estate.

#### 2.4.9 Document Management

- Documents uploaded at estate level or stage level
- Supported formats: PDF, DOC, DOCX, PNG, JPG, JPEG
- Stored in cloud storage with metadata (file name, type, size, description)
- Download by clicking filename; delete with confirmation

#### 2.4.10 Notifications

- In-app notification created when a pricing request is completed
- Links to the specific pricing request
- Sent to original requester (requester_id)
- Includes title and descriptive message with estate and lot info
- Read/unread status tracking

#### 2.4.11 Brand-Specific Logic

| Aspect | Hermitage Homes | Kingsbridge Homes |
|---|---|---|
| Required fields | BDM, Wholesale Group, Garage Side | None additional |
| Per-lot toggles | — | Custom House Design |
| Orientation | Displayed as read-only from lot data | — |
| Template | Separate template with own cell mappings | Separate template with own cell mappings |
| Data validations | house_type, facade_type, bdm, wholesale_group, garage_side | house_type, facade_type |

#### 2.4.12 Navigation Structure

| Page | Route | Description |
|---|---|---|
| Dashboard | `/` | Overview statistics and conflict summary |
| Upload | `/upload` | Excel file upload for package import |
| Pricing Requests | `/pricing` | Pricing request submission and tracking |
| Import Files | — | File import management |
| Estates & Rules | `/estates` | Estate, stage, lot, clash rule, and document management |
| Packages | `/packages` | Searchable table of all imported packages |
| Conflicts | `/conflicts` | Detected clashes based on clash rules |
| Admin | `/admin` | User management, pricing templates, and rule configuration (admin only) |

---

## 3. Data Architecture

### 3.1 Core Entity Model

The system has **15 core tables** spanning data aggregation, lot management, and packaging:

```
Developer --1:M--> Estate --1:M--> EstateStage --1:M--> StageLot
                     |                    |                  |
                     |                    |                  +--1:M--> HousePackage
                     |                    |                  |
                     |                    +--1:M--> ClashRule
                     |                    |
                     |                    +--M:1--> StagePricingRule
                     |
                     +--M:1--> Region
                     +--1:M--> EstateDocument
                     +--1:M--> Configuration

IngestionLog (standalone — references agent runs)
StatusHistory (lot status audit trail)
PricingRequest --M:1--> PricingTemplate
GlobalPricingRule --M:1--> PricingRuleCategory
Profile --1:M--> UserRole
Notification --M:1--> PricingRequest
```

### 3.2 Entity Definitions

#### Region

| Column | Type | Notes |
|---|---|---|
| region_id | PK | |
| name | varchar(255) | e.g., Western Melbourne, Northern Melbourne |
| created_at | timestamptz | UTC |

#### Developer

| Column | Type | Notes |
|---|---|---|
| developer_id | PK (serial/UUID) | |
| developer_name | varchar(255) | |
| developer_website | varchar(500) | Nullable |
| contact_email | varchar(255) | Nullable |
| notes | text | Nullable |
| created_at | timestamptz | UTC |
| updated_at | timestamptz | UTC |

#### Estate

| Column | Type | Notes |
|---|---|---|
| estate_id | PK (serial/UUID) | |
| developer_id | FK → Developer | |
| region_id | FK → Region | Nullable |
| estate_name | varchar(255) | |
| suburb | varchar(255) | Indexed for region filter |
| state | varchar(10) | e.g. VIC, NSW, QLD |
| postcode | varchar(10) | |
| contact_name | varchar(255) | Nullable |
| contact_mobile | varchar(50) | Nullable |
| contact_email | varchar(255) | Nullable |
| description | text | Nullable |
| active | boolean | Whether estate is still being monitored |
| notes | text | Nullable |
| created_at | timestamptz | UTC |
| updated_at | timestamptz | UTC |

#### EstateStage

| Column | Type | Notes |
|---|---|---|
| stage_id | PK | |
| estate_id | FK → Estate | |
| name | varchar(100) | e.g., "Stage 26", "Stage 27" |
| lot_count | integer | |
| status | enum | Active, Upcoming, Completed |
| release_date | date | Nullable |
| created_at | timestamptz | UTC |
| updated_at | timestamptz | UTC |

#### StageLot

| Column | Type | Notes |
|---|---|---|
| lot_id | PK | |
| stage_id | FK → EstateStage | |
| lot_number | varchar(50) | Unique per stage |
| frontage | decimal(8,2) | Width in metres. Nullable |
| depth | decimal(8,2) | Metres. Nullable |
| size_sqm | decimal(10,2) | Total lot area m². Nullable |
| corner_block | boolean | Default false |
| orientation | varchar(20) | e.g., N, NE, E, SE, S, SW, W, NW |
| side_easement | decimal(6,2) | Nullable |
| rear_easement | decimal(6,2) | Nullable |
| street_name | varchar(255) | Nullable |
| land_price | decimal(12,2) | Nullable |
| build_price | decimal(12,2) | Nullable |
| package_price | decimal(12,2) | Nullable |
| design | varchar(255) | Populated when package assigned. Nullable |
| facade | varchar(255) | Populated when package assigned. Nullable |
| brand | varchar(100) | Populated when package assigned. Nullable |
| status | enum | Available, Unavailable, Hold, Deposit Taken, Sold |
| substation | boolean | Default false |
| title_date | date | Expected or confirmed title date. Nullable |
| last_confirmed_date | timestamptz | Last date lot was seen in a data feed |
| source | enum | email, portal, website, pdf, manual |
| source_detail | varchar(500) | Specific URL, email address, or filename |
| created_at | timestamptz | UTC |
| updated_at | timestamptz | UTC |

**Constraints:**
- `UNIQUE (stage_id, lot_number)` — composite unique constraint
- `CHECK (land_price >= 0 OR land_price IS NULL)`
- No physical deletes — soft delete via status = Unavailable
- All datetime fields stored in UTC

#### StatusHistory

| Column | Type | Notes |
|---|---|---|
| history_id | PK | |
| lot_id | FK → StageLot | |
| previous_status | enum | |
| new_status | enum | |
| changed_at | timestamptz | UTC |
| triggering_agent | varchar(50) | email / scraper / portal / pdf / manual |
| source_detail | varchar(500) | Which specific source/run triggered the change |

#### HousePackage

| Column | Type | Notes |
|---|---|---|
| package_id | PK | |
| estate_id | FK → Estate | |
| stage_id | FK → EstateStage | |
| lot_number | varchar(50) | |
| design | varchar(255) | House design name |
| facade | varchar(255) | Facade type |
| colour_scheme | varchar(255) | Nullable |
| brand | varchar(100) | Hermitage Homes / Kingsbridge Homes |
| source | varchar(500) | Filename from which imported |
| status | varchar(50) | |
| flyer_path | varchar(500) | Cloud storage path to flyer document. Nullable |
| created_at | timestamptz | UTC |
| updated_at | timestamptz | UTC |

#### ClashRule

| Column | Type | Notes |
|---|---|---|
| rule_id | PK | |
| estate_id | FK → Estate | |
| stage_id | FK → EstateStage | |
| lot_number | varchar(50) | The lot this rule applies to |
| cannot_match | varchar[] | Array of lot numbers this lot cannot clash with |
| created_at | timestamptz | UTC |

**Constraints:**
- `UNIQUE (estate_id, stage_id, lot_number)`
- Rules are bidirectional in enforcement

#### PricingRequest

| Column | Type | Notes |
|---|---|---|
| request_id | PK | |
| requester_id | FK → Profile | |
| estate_id | FK → Estate | |
| stage_id | FK → EstateStage | |
| brand | varchar(100) | Hermitage Homes / Kingsbridge Homes |
| status | enum | Pending, In Progress, Completed |
| form_data | jsonb | Full submission form data (toggles, lot selections, brand-specific fields) |
| generated_file_path | varchar(500) | Cloud storage path to generated spreadsheet |
| completed_file_path | varchar(500) | Cloud storage path to uploaded completed sheet. Nullable |
| lot_numbers | varchar[] | Array of lot numbers in this request |
| submitted_at | timestamptz | UTC |
| completed_at | timestamptz | Nullable. UTC |
| created_at | timestamptz | UTC |
| updated_at | timestamptz | UTC |

#### PricingTemplate

| Column | Type | Notes |
|---|---|---|
| template_id | PK | |
| brand | varchar(100) | Hermitage Homes / Kingsbridge Homes |
| file_path | varchar(500) | Cloud storage path |
| sheet_name | varchar(100) | Target sheet in workbook |
| data_start_row | integer | Row where lot data begins |
| header_mappings | jsonb | Field name → cell (row, col) mappings |
| column_mappings | jsonb | Lot data field → column mappings |
| data_validations | jsonb | Extracted dropdown options per field |
| created_at | timestamptz | UTC |
| updated_at | timestamptz | UTC |

#### GlobalPricingRule

| Column | Type | Notes |
|---|---|---|
| rule_id | PK | |
| brand | varchar(100) | |
| item_name | varchar(255) | e.g., "Site Costs", "Corner Block Surcharge" |
| cost | decimal(12,2) | |
| condition | varchar(100) | Nullable. e.g., "corner_block", "building_crossover" |
| condition_value | varchar(255) | Nullable |
| cell_row | integer | Where item name is written |
| cell_col | integer | |
| cost_cell_row | integer | Where cost value is written |
| cost_cell_col | integer | |
| category_id | FK → PricingRuleCategory | Nullable |
| sort_order | integer | |
| created_at | timestamptz | UTC |
| updated_at | timestamptz | UTC |

#### StagePricingRule

Same structure as GlobalPricingRule, with additional:

| Column | Type | Notes |
|---|---|---|
| estate_id | FK → Estate | |
| stage_id | FK → EstateStage | |

#### PricingRuleCategory

| Column | Type | Notes |
|---|---|---|
| category_id | PK | |
| name | varchar(255) | |
| brand | varchar(100) | |
| sort_order | integer | |

#### Profile

| Column | Type | Notes |
|---|---|---|
| profile_id | PK | |
| email | varchar(255) | Unique |
| first_name | varchar(100) | |
| last_name | varchar(100) | |
| job_title | varchar(255) | Nullable |
| created_at | timestamptz | UTC |

#### UserRole

| Column | Type | Notes |
|---|---|---|
| user_role_id | PK | |
| profile_id | FK → Profile | |
| role | enum | admin, pricing, sales, requester |

**Constraint:** Minimum one role per user enforced at application layer.

#### Notification

| Column | Type | Notes |
|---|---|---|
| notification_id | PK | |
| profile_id | FK → Profile | Recipient |
| pricing_request_id | FK → PricingRequest | |
| title | varchar(255) | |
| message | text | |
| read | boolean | Default false |
| created_at | timestamptz | UTC |

#### EstateDocument

| Column | Type | Notes |
|---|---|---|
| document_id | PK | |
| estate_id | FK → Estate | |
| stage_id | FK → EstateStage | Nullable (estate-level if null) |
| file_name | varchar(255) | |
| file_type | varchar(50) | PDF, DOC, DOCX, PNG, JPG, JPEG |
| file_size | integer | Bytes |
| file_path | varchar(500) | Cloud storage path |
| description | text | Nullable |
| created_at | timestamptz | UTC |

#### IngestionLog

| Column | Type | Notes |
|---|---|---|
| log_id | PK | |
| agent_type | enum | email, scraper, portal, pdf |
| source_identifier | varchar(500) | URL, email address, folder path, portal name |
| run_timestamp | timestamptz | UTC |
| records_found | integer | |
| records_created | integer | |
| records_updated | integer | |
| records_deactivated | integer | Lots marked Unavailable this run |
| status | enum | success, partial, failed |
| error_detail | text | Nullable. Structured error info |

#### Configuration

| Column | Type | Notes |
|---|---|---|
| config_id | PK | |
| config_type | enum | email_account, website, portal, pdf_folder |
| estate_id | FK → Estate | Nullable (some configs span estates) |
| label | varchar(255) | Human-readable name |
| url_or_path | varchar(500) | Target URL or folder path |
| credentials_ref | varchar(255) | Reference to secrets vault — NEVER the credential itself |
| run_schedule | varchar(100) | Cron expression |
| enabled | boolean | Enable/disable without deleting config |
| priority_rank | integer | Source priority for conflict resolution |
| notes | text | Nullable |
| scraping_config | jsonb | Selectors, pagination rules, login form fields — varies by type |
| created_at | timestamptz | UTC |
| updated_at | timestamptz | UTC |

### 3.3 Database Indexing Strategy

The following indexes are required to meet performance targets:

| Index | Columns | Justification |
|---|---|---|
| idx_lot_stage_status | stage_id, status | Most common filter combination |
| idx_lot_price | land_price | Price range filtering |
| idx_lot_size | size_sqm | Lot size filtering |
| idx_lot_frontage | frontage | Frontage filtering |
| idx_lot_depth | depth | Depth filtering |
| idx_lot_title_date | title_date | Title date range filtering |
| idx_lot_stage_number | stage_id, lot_number | Unique constraint + lookup |
| idx_lot_status | status | Status filtering |
| idx_lot_last_confirmed | last_confirmed_date | Stale data detection |
| idx_estate_suburb | suburb | Region filtering |
| idx_estate_developer | developer_id | Developer lookup |
| idx_estate_region | region_id | Region grouping |
| idx_package_estate_stage | estate_id, stage_id | Package lookup per stage |
| idx_package_design_facade | design, facade | Clash detection |
| idx_clash_rule_estate_stage | estate_id, stage_id | Clash rule lookup |
| idx_pricing_request_requester | requester_id | User's own requests |
| idx_pricing_request_status | status | Status filtering |

### 3.4 Data Integrity Rules

1. **Composite uniqueness** — lot_number + stage_id must be unique.
2. **Non-negative prices** — land_price, build_price, package_price must be >= 0 or NULL.
3. **Status history logging** — every status transition must be recorded in StatusHistory with timestamp and triggering agent.
4. **UTC storage** — all datetime fields stored in UTC. Application layer handles AEST/AEDT display conversion.
5. **Soft deletes** — lots are never physically deleted. Status = Unavailable preserves historical data.
6. **Credential isolation** — Configuration.credentials_ref stores a vault key reference only. Credentials never stored in the database.
7. **Clash rule uniqueness** — (estate_id, stage_id, lot_number) unique constraint on clash rules.
8. **Role minimum** — every user must have at least one role assigned.
9. **Cascade deletes** — deleting an estate cascades to stages, lots, packages, and clash rules.

---

## 4. Technical Architecture

### 4.1 Architecture Style

**Decision: Python-first modular monolith with agent subsystem.**

- **PoC:** Deployed on **Railway** for rapid iteration and cost-effective hosting.
- **Production (future):** Migrated to **Microsoft Azure** for enterprise-grade infrastructure, compliance, and scalability.

The monolith pattern keeps the API layer, agent orchestrator, packaging engine, and individual agents in a single deployable service, minimising Railway service costs. A separate PostgreSQL plugin and Railway Volume provide data and file storage.

### 4.2 Railway PoC Architecture

```
+----------------------------------------------------------------------+
|                        Railway Project                                |
+----------------------------------------------------------------------+
|                                                                      |
|  +-----------------------------+   +------------------------------+  |
|  |  Service: API               |   |  Service: Frontend           |  |
|  |  (Docker — FastAPI)         |   |  (Nixpacks — React + Vite)   |  |
|  |                             |   |  Served as static build      |  |
|  |  - REST API endpoints       |   |  via Railway or Vite preview |  |
|  |  - Packaging engine         |   +------------------------------+  |
|  |  - Agent orchestrator       |                                     |
|  |  - APScheduler (cron)       |                                     |
|  |  - Playwright (headless)    |                                     |
|  |                             |                                     |
|  |  [Railway Volume]           |                                     |
|  |  /data/storage/             |                                     |
|  |  - PDF archive & inbox      |                                     |
|  |  - Pricing templates        |                                     |
|  |  - Generated spreadsheets   |                                     |
|  |  - Estate documents         |                                     |
|  |  - Package flyers           |                                     |
|  |  - Export files             |                                     |
|  +-------------+---------------+                                     |
|                |                                                     |
|  +-------------v---------------+                                     |
|  |  Plugin: PostgreSQL         |                                     |
|  |  - All application data     |                                     |
|  |  - Automated backups        |                                     |
|  +-----------------------------+                                     |
+----------------------------------------------------------------------+

Secrets: Railway environment variables (encrypted at rest)
CI/CD:   GitHub Actions → Railway auto-deploy on push to main
Domain:  Railway-provided *.up.railway.app (custom domain optional)
```

**Why a single API service (not separate API + Orchestrator + Agent services):**

Railway bills per service. Consolidating API, orchestrator, and agents into one service with APScheduler for cron-based agent runs is the most cost-effective approach for a PoC. Agents run as background tasks within the same process. If agent workloads grow, they can be split into separate Railway services later.

### 4.3 Component Decisions

| Decision | Choice | Rationale |
|---|---|---|
| **Language** | Python 3.12+ | LLM libraries (LangChain/LangGraph), web scraping (Playwright), PDF extraction (pdfplumber), Excel generation (openpyxl), and data handling (pandas, SQLAlchemy) are all Python-native. |
| **API Framework** | FastAPI | Async-native, automatic OpenAPI spec generation, Pydantic validation for query parameters — ideal for both LSI and packaging API endpoints. |
| **ORM / Migrations** | SQLAlchemy 2.0 + Alembic | Mature, well-documented, excellent PostgreSQL support. Type-annotated models with SQLAlchemy 2.0 mapped_column syntax. |
| **Database** | Railway PostgreSQL plugin | Managed PostgreSQL with automated backups. Superior jsonb support for template mappings and form data. Zero-config connection via `DATABASE_URL` env var. |
| **Agent Orchestration** | APScheduler (in-process) or custom Python task runner | Lightweight in-process scheduler for cron-based agent runs. Avoids the cost of separate worker services on Railway. LangGraph evaluated for production. |
| **Web Scraping** | Playwright (Python) | For JS-heavy sites. Runs in headless Chromium within the Docker container. |
| **PDF Extraction** | pdfplumber + Tesseract OCR | pdfplumber for text-based PDFs; Tesseract OCR for scanned documents. Avoids cloud OCR service costs for PoC. |
| **Excel Generation** | openpyxl | Reading/writing .xlsx/.xlsm files for pricing template management and spreadsheet generation. |
| **AI Extraction (LLM)** | Anthropic Claude API (Sonnet) | Claude Sonnet for structured extraction from unstructured text. Schema-constrained JSON output with confidence scoring. |
| **Email Access** | Microsoft Graph API or IMAP | Graph API for M365 mailboxes; IMAP as fallback for other providers. |
| **Frontend** | React + Vite + shadcn/ui + Tailwind CSS | TanStack Table for data tables. Deployed as a separate Railway service (Nixpacks static build). |
| **Task Scheduling** | APScheduler (in-process) | Runs within the API service. Cron expressions configure agent run intervals. No separate worker service needed. |
| **Secrets Management** | Railway environment variables | Encrypted at rest. Accessed via `os.environ`. Sufficient for PoC; migrate to dedicated vault for production. |
| **File Storage** | Railway Volume | Persistent volume mounted at `/data/storage/`. Stores PDFs, templates, generated sheets, documents, flyers, exports. Sufficient for PoC volumes. |
| **Authentication** | Email/password (self-managed) | JWT-based auth with bcrypt password hashing. Role-based access via user_roles table. SSO deferred to production. |
| **Monitoring** | Structured logging + Railway metrics | Python `structlog` for JSON-formatted logs. Railway provides built-in CPU/memory/network metrics and log aggregation. |
| **CI/CD** | GitHub Actions + Railway auto-deploy | Push to main triggers Railway deployment. GitHub Actions for lint, test, build. |

### 4.4 Security Architecture

| Layer | Requirement | PoC Implementation |
|---|---|---|
| Credential storage | Encrypted secrets vault. Never in plain text or source code. | Railway environment variables (encrypted at rest) |
| Access control | RBAC: read-only for consultants, admin/pricing/sales/requester for packaging | JWT auth + application-layer role mapping via user_roles table |
| Credential exposure prevention | Credentials must not appear in logs, config files, API responses, or UI after initial entry | Environment variable references only in Configuration table. Log redaction middleware. |
| Data durability | Daily backups. Point-in-time recovery available. | Railway PostgreSQL automated backups |
| Network isolation | DB not publicly exposed | Railway internal networking. PostgreSQL accessible only via private Railway network. |
| Transit encryption | HTTPS only | Railway provides automatic HTTPS with TLS termination on all services. |
| SQL injection prevention | Parameterised queries or ORM | SQLAlchemy ORM — never string-interpolated SQL |
| Input validation | All query params validated server-side. Malformed = 400. | Pydantic models for FastAPI request validation |
| Role enforcement | Pricing/admin features restricted by role | user_roles table checked on every privileged operation |
| Email verification | Users must verify email before sign-in | Auto-confirm disabled in auth configuration |

---

## 5. Claude Code Agent Team Breakdown

### 5.1 Agent Team Architecture

The development team consists entirely of **Claude Code agents** orchestrated through a structured task breakdown. Each agent operates on a well-defined work package with clear inputs, outputs, and acceptance criteria.

```
+----------------------------------------------------------+
|                   HUMAN TECH LEAD                         |
|         (Reviews PRs, makes architecture calls,          |
|          resolves ambiguity, owns deployment)             |
+----------------------------+-----------------------------+
                             | Directs
          +------------------+------------------+
          |                  |                  |
+---------v--------+ +------v---------+ +------v-----------+
|  ORCHESTRATOR    | |  SPECIALIST    | |  QUALITY          |
|  AGENT           | |  AGENTS        | |  AGENTS           |
|  (Planning,      | |  (Feature      | |  (Testing,        |
|   scaffolding,   | |   implemen-    | |   documentation,  |
|   integration)   | |   tation)      | |   review)         |
+------------------+ +----------------+ +-------------------+
```

### 5.2 Agent Roles and Responsibilities

#### Agent 0 — Project Scaffolder (run once at project start)

| Aspect | Detail |
|---|---|
| **Purpose** | Bootstrap the repository structure, tooling, and CI/CD pipeline |
| **Inputs** | This PROJECT_SETUP.md, the BRD, PackagingRequirements |
| **Outputs** | Repository skeleton, pyproject.toml, Docker configs, Railway config, Alembic setup, pre-commit config, GitHub Actions workflows |
| **Key Tasks** | Create directory structure (see §9). Configure linting (ruff), formatting (black), type checking (mypy). Set up Docker Compose for local dev (PostgreSQL + Playwright). Configure Railway services (API + Frontend + PostgreSQL). Create initial Alembic migration from entity definitions. |

#### Agent 1 — Data Layer Agent

| Aspect | Detail |
|---|---|
| **Purpose** | Implement the database schema, ORM models, repositories, and data access patterns |
| **Inputs** | Entity definitions from §3.2, data integrity rules from §3.4, indexing strategy from §3.3 |
| **Outputs** | SQLAlchemy models (all 15 tables), Alembic migrations, repository classes, database seed scripts |
| **Key Tasks** | Define all models with proper types, constraints, and relationships. Create composite unique constraints. Implement StatusHistory trigger/hook. Build repository pattern with typed query methods for both LSI filter API and packaging operations. Create seed data for development. |

#### Agent 2 — API Layer Agent

| Aspect | Detail |
|---|---|
| **Purpose** | Implement the FastAPI REST API endpoints for the LSI, packaging system, and admin operations |
| **Inputs** | API endpoint spec from Addendum A, PackagingRequirements sections 6-10 |
| **Outputs** | FastAPI routers, Pydantic request/response schemas, middleware (auth, error handling, logging) |
| **Key Tasks** | LSI endpoints (lots, estates, regions, export). Packaging endpoints (pricing requests CRUD, clash rule validation, spreadsheet generation/download, package import, template management, pricing rules CRUD). Admin endpoints (user management, role assignment). Role-based access control middleware. |

#### Agent 3 — Email Reader Agent Developer

| Aspect | Detail |
|---|---|
| **Purpose** | Build the email ingestion agent |
| **Inputs** | BRD §5.1, §8.2, §8.3, §9.3 |
| **Outputs** | Email reader agent module, LLM extraction prompts, attachment parsers, message ID dedup logic |

#### Agent 4 — Web Scraper Agent Developer

| Aspect | Detail |
|---|---|
| **Purpose** | Build the configurable web scraping agent |
| **Inputs** | BRD §5.2, §8.2, §9.1 |
| **Outputs** | Web scraper agent module, Playwright automation scripts, selector engine, AI fallback parser |

#### Agent 5 — Portal Access Agent Developer

| Aspect | Detail |
|---|---|
| **Purpose** | Build the authenticated portal access agent |
| **Inputs** | BRD §5.3, §8.2, §9.2 |
| **Outputs** | Portal access agent module, login automation, session management, credential retrieval from environment |

#### Agent 6 — PDF Pickup Agent Developer

| Aspect | Detail |
|---|---|
| **Purpose** | Build the PDF monitoring and extraction agent |
| **Inputs** | BRD §5.4, §8.2, §8.3, §9.4 |
| **Outputs** | PDF pickup agent module, folder monitor, OCR pipeline, AI extraction prompts, archive manager |

#### Agent 7 — Orchestrator Developer

| Aspect | Detail |
|---|---|
| **Purpose** | Build the central orchestration layer that coordinates all ingestion agents |
| **Inputs** | BRD §5.5, §5.6, §8.1 |
| **Outputs** | Orchestrator service, scheduler, conflict resolution engine, lot status lifecycle engine, alerting |

#### Agent 8 — Frontend Agent

| Aspect | Detail |
|---|---|
| **Purpose** | Build the complete frontend application (LSI + Packaging System) |
| **Inputs** | Addendum A (LSI spec), PackagingRequirements (all sections), Reference screenshots |
| **Outputs** | React application with: LSI (filter panel, results table, lot detail, export), Dashboard, Estates & Rules management, Pricing Request submission & tracking, Package browsing, Conflict detection display, Admin panel (users, templates, pricing rules), Upload page, Notifications |
| **Key Tasks** | React + Vite + shadcn/ui + Tailwind scaffold. Sidebar navigation (Dashboard, Upload, Pricing Requests, Import Files, Estates & Rules, Packages, Conflicts, Admin). LSI two-panel layout with all 8 filter types. Estate/stage/lot management with inline editing. Pricing request form with brand-specific fields, validated dropdowns from template data validations, multi-lot card interface. Clash rule management with copy-to-stage functionality. Visual Excel cell mapper for template configuration. Pricing rules management with inline editing and duplication. Package table with search/filter. Conflict detection display. Notification system with read/unread tracking. Responsive design. |

#### Agent 9 — Packaging Engine Agent

| Aspect | Detail |
|---|---|
| **Purpose** | Build the Excel spreadsheet generation engine and clash validation logic |
| **Inputs** | PackagingRequirements sections 6-9 |
| **Outputs** | Spreadsheet generator, clash rule validator, pricing rule evaluator, template parser, data validation extractor |
| **Key Tasks** | openpyxl-based spreadsheet generation from brand templates. Cell mapping injection (header + lot data rows). Conditional pricing rule evaluation with RequestContext. Clash rule validation (two-pass: within-request + against existing packages). Template upload with data validation extraction. Package import from completed Excel files. |

#### Agent 10 — Test Agent

| Aspect | Detail |
|---|---|
| **Purpose** | Write comprehensive automated tests across all layers |
| **Inputs** | BRD acceptance criteria, PackagingRequirements, all module implementations |
| **Outputs** | Unit tests, integration tests, E2E tests, test fixtures, CI test pipeline configuration |
| **Key Tasks** | Unit tests for status lifecycle, conflict resolution, clash rule validation, pricing rule evaluation, spreadsheet generation. Integration tests for all API endpoints, agent pipelines, and packaging workflow. E2E tests for LSI journeys and pricing request submission flow. Performance tests. Security tests. |

#### Agent 11 — Documentation Agent

| Aspect | Detail |
|---|---|
| **Purpose** | Generate and maintain all project documentation |
| **Inputs** | All code, BRD, PackagingRequirements, architecture decisions, test results |
| **Outputs** | API docs, data dictionary, ADRs, runbooks, onboarding guide, LSI user guide, packaging user guide |

### 5.3 Agent Execution Order

```
Phase 1 — Foundation
  Agent 0: Project Scaffolder
    +---> Agent 1: Data Layer (all 15 tables)
           +---> Agent 2: API Layer (LSI + Packaging + Admin endpoints)
                  +---> Agent 8: Frontend (LSI + Packaging UI)

Phase 2 — Packaging Engine (can start after Agent 1)
  Agent 9: Packaging Engine (spreadsheet gen, clash validation, pricing rules)

Phase 3 — Ingestion Agents (parallelisable, after Agent 1)
  +-- Agent 3: Email Reader --+
  +-- Agent 4: Web Scraper  --+
  +-- Agent 5: Portal Access --+---> Agent 7: Orchestrator (integrates all agents)
  +-- Agent 6: PDF Pickup   --+

Phase 4 — Quality and Documentation (after all code)
  +-- Agent 10: Test Agent --+
  +-- Agent 11: Documentation Agent --+
```

### 5.4 Human Tech Lead Responsibilities

| Responsibility | Why It Cannot Be Delegated |
|---|---|
| Architecture decision arbitration | Trade-off analysis requires business context and judgement |
| PR review and merge approval | Final quality gate — AI agents can miss subtle integration issues |
| Per-site scraper/portal configuration tuning | Requires live browser interaction with real developer websites and portals |
| LLM prompt tuning for extraction | Requires reviewing real-world email/PDF samples and iterating on accuracy |
| Railway project and resource provisioning | Requires account access and budget approval |
| Credential management | Portal logins and email account credentials — security-sensitive |
| Legal review of scraping permissions | Per-estate ToS review |
| Pricing template configuration | Requires understanding of brand-specific Excel template layouts |
| UAT coordination with consultants and sales teams | End-user validation requires human relationships |
| Production deployment and monitoring | Go/no-go decisions, incident response |

---

## 6. Testing Strategy

### 6.1 Test Pyramid

```
          /  E2E Tests (LSI + Packaging user journeys)  \     ~10%
         /   Integration Tests (agents + API + packaging) \    ~30%
        /    Unit Tests (logic + models + engine)           \   ~60%
```

### 6.2 Acceptance Criteria to Test Mapping

#### Core System Acceptance Criteria (BRD §10)

| # | Criterion | Test Type | Test ID |
|---|---|---|---|
| AC-01 | Email agent: extract lot fields from email body/attachment, insert/update in DB within one run cycle | Integration | `EMAIL-INT-001` |
| AC-02 | Web scraper: scrape configured URL, store lots with correct field mapping | Integration | `SCRAPE-INT-001` |
| AC-03 | Portal agent: log in with credentials, navigate, extract lot data without human intervention | Integration | `PORTAL-INT-001` |
| AC-04 | PDF agent: detect PDF in monitored folder, extract lot data, insert records | Integration | `PDF-INT-001` |
| AC-05 | Status lifecycle: lot present in run N but absent in run N+1 → status = Unavailable within one cycle | Unit + Integration | `STATUS-UNIT-001`, `STATUS-INT-001` |
| AC-06 | Data integrity: no duplicate lot_number + stage_id combinations in DB | Unit + DB constraint | `DATA-UNIT-001` |
| AC-07 | Configuration: add new estate website and scrape it without code changes — config only | E2E | `CONFIG-E2E-001` |
| AC-08 | Conflict resolution: same lot in two sources → apply source priority, log resolution decision | Unit + Integration | `CONFLICT-UNIT-001`, `CONFLICT-INT-001` |
| AC-09 | Logging: every agent run produces structured IngestionLog entry | Integration | `LOG-INT-001` |
| AC-10 | Security: portal credentials not visible in any log, config file, API response, or UI after entry | Security | `SEC-001` |

#### LSI Acceptance Criteria (Addendum A §7)

| # | Criterion | Test Type | Test ID |
|---|---|---|---|
| AC-11 | Filter — Estate: selecting estates filters results correctly with updated count | E2E | `LSI-E2E-001` |
| AC-12 | Filter — Region: selecting suburb/region filters to matching estate lots | E2E | `LSI-E2E-002` |
| AC-13 | Filter — Price Range: min/max filters lots correctly, null prices excluded unless toggled | E2E + Unit | `LSI-E2E-003`, `API-UNIT-001` |
| AC-14 | Filter — Lot Size: min/max m² returns matching lots only | E2E | `LSI-E2E-004` |
| AC-15 | Filter — Frontage: min frontage returns lots >= value | E2E | `LSI-E2E-005` |
| AC-16 | Filter — Depth: min depth returns lots >= value | E2E | `LSI-E2E-006` |
| AC-17 | Filter — Combined: any combination produces correct intersection | E2E + Integration | `LSI-E2E-007`, `API-INT-001` |
| AC-18 | Sorting: column header click sorts server-side, second click reverses | E2E | `LSI-E2E-008` |
| AC-19 | Pagination: page navigation correct, page size selector works | E2E | `LSI-E2E-009` |
| AC-20 | URL State: filters update URL; pasting URL reproduces filtered view | E2E | `LSI-E2E-010` |
| AC-21 | Lot Detail: row click opens detail panel, close returns with filters intact | E2E | `LSI-E2E-011` |
| AC-22 | Export: CSV download contains ALL matching records (not just current page), timestamped filename | E2E + Integration | `LSI-E2E-012`, `EXPORT-INT-001` |
| AC-23 | Stale Data Warning: lots with Last Confirmed Date > 7 days show visual warning | E2E | `LSI-E2E-013` |
| AC-24 | Empty State: no matching lots → helpful message with filter adjustment prompt | E2E | `LSI-E2E-014` |
| AC-25 | Performance: filtered results load within 1 second at 50,000 records | Performance | `PERF-001` |
| AC-26 | Authentication: unauthenticated access redirected to login | Security | `SEC-002` |

#### Packaging System Acceptance Criteria

| # | Criterion | Test Type | Test ID |
|---|---|---|---|
| AC-27 | Pricing request submission generates pre-filled Excel spreadsheet from brand template | Integration | `PKG-INT-001` |
| AC-28 | Clash rule validation blocks submission when same design+facade on adjacent lots (within request) | Unit + Integration | `CLASH-UNIT-001`, `CLASH-INT-001` |
| AC-29 | Clash rule validation blocks submission when same design+facade conflicts with existing packages | Unit + Integration | `CLASH-UNIT-002`, `CLASH-INT-002` |
| AC-30 | Pricing rules with conditions are correctly evaluated against RequestContext | Unit | `RULE-UNIT-001` |
| AC-31 | Global and stage-level pricing rules both inject into generated spreadsheet at correct cells | Integration | `RULE-INT-001` |
| AC-32 | Template data validations extracted and populate dropdown options in submission form | Integration | `TMPL-INT-001` |
| AC-33 | Package import from Excel correctly creates HousePackage records and updates StageLot fields | Integration | `PKG-INT-002` |
| AC-34 | Conflict detection identifies all design+facade clashes across packages per clash rules | Unit + E2E | `CONFLICT-UNIT-002`, `CONFLICT-E2E-001` |
| AC-35 | Clash rules can be copied between stages/estates without duplicates | Integration | `CLASH-INT-003` |
| AC-36 | Role-based access: non-admin users cannot access admin features | Security + E2E | `SEC-003`, `ROLE-E2E-001` |
| AC-37 | Notification sent to requester when pricing request completed | Integration | `NOTIF-INT-001` |
| AC-38 | Brand-specific fields enforced: Hermitage requires BDM/Wholesale Group/Garage Side | E2E | `BRAND-E2E-001` |
| AC-39 | Completed pricing request upload extracts and imports packages into database | Integration | `PKG-INT-003` |
| AC-40 | Estate deletion cascades to stages, lots, packages, and clash rules | Integration | `CASCADE-INT-001` |

### 6.3 Testing by Layer

| Layer | Tooling | Focus |
|---|---|---|
| **Unit** | pytest + pytest-asyncio | Status lifecycle rules, conflict resolution, clash rule validation, pricing rule evaluation, spreadsheet generation logic, data normalisation |
| **Integration** | pytest + httpx (TestClient) + testcontainers-python | API endpoint filter combinations, agent ingestion pipelines with mocked sources, packaging workflow, DB operations |
| **E2E** | Playwright (Python) | Full LSI user journeys, pricing request submission flow, clash rule management, package browsing |
| **Performance** | Locust or k6 | API response time at 50,000 lots. Export generation for 5,000 records. Spreadsheet generation time. |
| **Security** | Manual + automated | Credential exposure scan, auth enforcement, role-based access, SQL injection via malformed params |

### 6.4 Environment Strategy

| Environment | Purpose | Data | Hosting |
|---|---|---|---|
| **Local** | Developer/agent workstation. Docker Compose: PostgreSQL + Azurite + Playwright | Seed: 10 estates, 200 lots, sample packages and clash rules | Docker |
| **Dev/PoC** | Continuous integration. Deploy on merge to main | Seed + synthetic (1,000 lots) | Railway (Hobby plan) |
| **Staging** | Pre-production. Mirrors production config | Anonymised production-like snapshot | Railway (Pro plan) |
| **Production** | Live system with real agent runs | Real ingested data | Azure (future) or Railway (Pro plan) |

---

## 7. Deployment Architecture

### 7.1 Railway PoC Configuration

The PoC uses Railway's project structure with minimal services for cost efficiency:

```
Railway Project: house-and-land-packager
|
+-- Service: api (Docker)
|   - Dockerfile.api
|   - Port: 8000
|   - Volume: /data/storage (10 GB)
|   - Environment variables: DATABASE_URL, SECRET_KEY, ANTHROPIC_API_KEY, etc.
|   - Health check: /api/health
|   - Auto-deploy: on push to main
|
+-- Service: frontend (Nixpacks)
|   - Root: /frontend
|   - Build: npm run build
|   - Port: 5173 (preview) or static serve
|   - Environment variables: VITE_API_URL
|   - Auto-deploy: on push to main
|
+-- Plugin: PostgreSQL
    - Auto-provisioned
    - DATABASE_URL injected automatically
    - Automated daily backups
```

**Railway Volume layout (`/data/storage/`):**

```
/data/storage/
+-- pdf-inbox/              # Incoming PDFs for pickup agent
+-- pdf-archive/            # Processed PDFs
+-- pricing-templates/      # Brand Excel templates (.xlsx/.xlsm)
+-- generated-sheets/       # Auto-generated pricing spreadsheets
+-- completed-sheets/       # Uploaded completed pricing sheets
+-- estate-documents/       # Estate/stage-level documents
+-- package-flyers/         # Package flyer attachments
+-- exports/                # CSV/XLSX export staging
+-- attachments/            # Email attachment cache
```

### 7.2 CI/CD Pipeline (GitHub Actions + Railway)

```
Code Push (main)
  |
  +-->  GitHub Actions:
  |     +-->  Lint + Type Check (ruff, mypy)
  |     +-->  Unit Tests (pytest)
  |     +-->  Build check (Docker build, npm build)
  |
  +-->  Railway auto-deploy (triggered on push):
         +-->  Build & deploy API service (Docker)
         +-->  Build & deploy Frontend service (Nixpacks)
         +-->  Run Alembic migrations (release command)
         +-->  Health check verification
```

### 7.3 Railway Cost Estimation (Monthly — USD)

| Service | Tier | Est. Monthly Cost |
|---|---|---|
| Railway Hobby Plan | Base subscription | $5 |
| API Service | ~0.5 vCPU, 512 MB RAM avg | $5-$15 |
| Frontend Service | Static build, minimal resources | $1-$3 |
| PostgreSQL Plugin | ~256 MB RAM, 1 GB storage | $5-$10 |
| Railway Volume | 10 GB persistent storage | Included |
| Anthropic API (Claude Sonnet) | Pay-per-token for LLM extraction | $5-$30 |
| **Total Estimate** | | **$21-$63 /month** |

**Cost-saving measures:**

- Single API service consolidates API + orchestrator + agents (avoids 3+ separate service costs)
- Railway Volume for file storage instead of a paid object storage service
- Tesseract OCR (open source, in-container) instead of paid cloud OCR
- APScheduler in-process instead of separate cron job services
- JWT self-managed auth instead of a paid auth service
- Railway Hobby plan ($5/month) includes $5 of resource usage

**Scaling to Railway Pro plan ($20/month) when needed for:**
- Higher resource limits (8 GB RAM, 8 vCPU per service)
- Team collaboration features
- Multiple environments (staging + production)

### 7.4 Future Azure Production Architecture

When the PoC is validated and ready for production, the system will migrate to Azure for enterprise features:

| PoC (Railway) | Production (Azure) |
|---|---|
| Railway PostgreSQL plugin | Azure Database for PostgreSQL (Flexible Server) — HA, VNet, 35-day backup retention |
| Railway Volume | Azure Blob Storage — lifecycle policies, geo-redundancy, CDN integration |
| Railway env vars | Azure Key Vault — managed identity, rotation policies, audit logging |
| Railway auto-deploy | Azure Container Apps — consumption billing, scale to zero, built-in cron jobs |
| Self-managed JWT auth | Microsoft Entra ID — SSO, MFA, enterprise directory integration |
| Railway metrics + logs | Azure Application Insights + Log Analytics — custom dashboards, alert rules |
| N/A | Azure Front Door — WAF, CDN, DDoS protection |
| N/A | Azure Service Bus — durable message queues for agent task dispatch |
| Tesseract OCR | Azure Document Intelligence — superior accuracy for complex PDF layouts |

Azure production cost estimate: **$250-$680 AUD/month** (see ADR-016 for migration criteria).

---

## 8. Documentation Strategy

### 8.1 Documentation as Code

| Document | Format | Location | Owner Agent | Update Trigger |
|---|---|---|---|---|
| Architecture Decision Records | Markdown (ADR template) | `/docs/adr/` | Agent 11 (Documentation) | Any architecture decision |
| API Reference | OpenAPI 3.1 YAML (auto-generated by FastAPI) | `/docs/api/openapi.yaml` | Auto-generated | Every API change |
| Data Dictionary | Markdown (generated from SQLAlchemy models) | `/docs/data/data-dictionary.md` | Agent 11 | Every schema migration |
| Entity Relationship Diagram | Mermaid in Markdown | `/docs/data/erd.md` | Agent 11 | Every schema migration |
| Agent Configuration Guide | Markdown | `/docs/operations/agent-config.md` | Agent 11 | New source type or config change |
| Agent Runbooks | Markdown | `/docs/operations/runbooks/` | Agent 11 | New operational procedure |
| LSI User Guide | Markdown | `/docs/user-guide/lsi.md` | Agent 11 | Every LSI feature change |
| Packaging User Guide | Markdown | `/docs/user-guide/packaging.md` | Agent 11 | Every packaging feature change |
| Test Plan and Traceability Matrix | Markdown | `/docs/testing/` | Agent 10 (Test) | Every sprint |
| Onboarding Guide | Markdown | `/docs/onboarding.md` | Agent 11 | Quarterly |
| Release Notes | Markdown | `/docs/releases/` | Agent 11 | Every release |
| LLM Prompt Templates | Markdown + JSON | `/docs/prompts/` | Agents 3, 4, 5, 6 | Prompt tuning iterations |

### 8.2 Documentation Standards

1. Every PR must include documentation updates if the change affects API contracts, data schema, agent behaviour, packaging workflow, or user-facing features.
2. ADRs are immutable — superseded decisions get a new ADR referencing the old one.
3. The OpenAPI spec is auto-generated by FastAPI from Pydantic models — never manually maintained.
4. The data dictionary is generated from SQLAlchemy model introspection — a CI step ensures it stays in sync.
5. LLM prompt templates are version-controlled with sample inputs/outputs for each iteration.

---

## 9. Repository Structure

```
house-and-land-packager/
+-- .github/workflows/          # GitHub Actions CI/CD
|   +-- ci.yml                  # Lint, test, build
|   +-- deploy-dev.yml          # Auto-deploy to dev
|   +-- deploy-staging.yml      # Manual gate to staging
|   +-- deploy-prod.yml         # Manual gate to production
+-- docs/                       # All documentation (see §8.1)
|   +-- adr/
|   +-- api/
|   +-- data/
|   +-- operations/
|   +-- prompts/
|   +-- testing/
|   +-- user-guide/
|   +-- releases/
+-- railway.toml                # Railway service configuration
+-- infra/                      # Future Azure Bicep IaC (production)
+-- src/
|   +-- hlp/                    # Main Python package
|   |   +-- __init__.py
|   |   +-- config.py           # Settings (pydantic-settings, env vars)
|   |   +-- database.py         # SQLAlchemy engine, session factory
|   |   |
|   |   +-- models/             # SQLAlchemy ORM models
|   |   |   +-- region.py
|   |   |   +-- developer.py
|   |   |   +-- estate.py
|   |   |   +-- estate_stage.py
|   |   |   +-- stage_lot.py
|   |   |   +-- status_history.py
|   |   |   +-- house_package.py
|   |   |   +-- clash_rule.py
|   |   |   +-- pricing_request.py
|   |   |   +-- pricing_template.py
|   |   |   +-- pricing_rule.py
|   |   |   +-- pricing_rule_category.py
|   |   |   +-- profile.py
|   |   |   +-- user_role.py
|   |   |   +-- notification.py
|   |   |   +-- estate_document.py
|   |   |   +-- ingestion_log.py
|   |   |   +-- configuration.py
|   |   |
|   |   +-- repositories/       # Data access layer (typed queries)
|   |   |   +-- lot_repository.py       # Complex filter queries for LSI
|   |   |   +-- estate_repository.py
|   |   |   +-- stage_repository.py
|   |   |   +-- package_repository.py
|   |   |   +-- clash_rule_repository.py
|   |   |   +-- pricing_request_repository.py
|   |   |   +-- config_repository.py
|   |   |   +-- ingestion_log_repository.py
|   |   |
|   |   +-- api/                # FastAPI application
|   |   |   +-- main.py         # App factory, middleware, CORS
|   |   |   +-- dependencies.py # DB session, auth dependencies
|   |   |   +-- routers/
|   |   |   |   +-- lots.py     # GET /api/lots, /api/lots/:id, /api/lots/export
|   |   |   |   +-- estates.py  # GET /api/estates, CRUD operations
|   |   |   |   +-- stages.py   # Stage management
|   |   |   |   +-- regions.py  # GET /api/regions
|   |   |   |   +-- packages.py # Package browsing, import, delete
|   |   |   |   +-- pricing.py  # Pricing request CRUD, spreadsheet gen/download
|   |   |   |   +-- clash_rules.py # Clash rule management, copy
|   |   |   |   +-- pricing_rules.py # Global + stage pricing rules
|   |   |   |   +-- templates.py # Pricing template management
|   |   |   |   +-- conflicts.py # Conflict detection
|   |   |   |   +-- admin.py    # User management, role assignment
|   |   |   |   +-- notifications.py # Notification read/list
|   |   |   |   +-- documents.py # Estate document upload/download
|   |   |   +-- schemas/        # Pydantic request/response models
|   |   |       +-- lot_schemas.py
|   |   |       +-- estate_schemas.py
|   |   |       +-- package_schemas.py
|   |   |       +-- pricing_schemas.py
|   |   |       +-- clash_schemas.py
|   |   |       +-- user_schemas.py
|   |   |       +-- common.py   # Pagination, error responses
|   |   |
|   |   +-- agents/             # Ingestion agents
|   |   |   +-- base.py         # BaseAgent ABC (shared interface, dry-run, JSON output)
|   |   |   +-- email_reader.py
|   |   |   +-- web_scraper.py
|   |   |   +-- portal_access.py
|   |   |   +-- pdf_pickup.py
|   |   |   +-- extraction/     # AI extraction pipeline
|   |   |       +-- llm_extractor.py
|   |   |       +-- prompts/
|   |   |       +-- schema_validator.py
|   |   |       +-- confidence.py
|   |   |
|   |   +-- orchestrator/       # Agent coordination
|   |   |   +-- scheduler.py
|   |   |   +-- dispatcher.py
|   |   |   +-- normaliser.py
|   |   |   +-- conflict.py
|   |   |   +-- lifecycle.py
|   |   |   +-- alerting.py
|   |   |
|   |   +-- packaging/          # House & Land packaging engine
|   |   |   +-- spreadsheet_generator.py  # openpyxl-based Excel generation
|   |   |   +-- template_parser.py        # Template upload, validation extraction
|   |   |   +-- cell_mapper.py            # Cell mapping logic
|   |   |   +-- clash_validator.py        # Two-pass clash rule validation
|   |   |   +-- pricing_evaluator.py      # Conditional pricing rule evaluation
|   |   |   +-- package_importer.py       # Package extraction from completed sheets
|   |   |   +-- conflict_detector.py      # Cross-package conflict detection
|   |   |
|   |   +-- shared/             # Cross-cutting concerns
|   |       +-- auth.py         # JWT auth + role checking
|   |       +-- logging.py      # Structured logging config (structlog)
|   |       +-- storage.py      # File storage abstraction (Railway Volume / Azure Blob)
|   |       +-- export.py       # CSV/XLSX generation
|   |
|   +-- migrations/             # Alembic migrations
|       +-- alembic.ini
|       +-- env.py
|       +-- versions/
|
+-- frontend/                   # React application
|   +-- src/
|   |   +-- App.tsx
|   |   +-- components/
|   |   |   +-- layout/         # Sidebar navigation, header
|   |   |   +-- dashboard/      # Dashboard stats, conflict summary
|   |   |   +-- lsi/            # Land Search Interface
|   |   |   |   +-- FilterPanel/
|   |   |   |   +-- ResultsTable/
|   |   |   |   +-- LotDetailPanel/
|   |   |   |   +-- SearchBar/
|   |   |   |   +-- ExportButton/
|   |   |   +-- estates/        # Estate, stage, lot management
|   |   |   +-- pricing/        # Pricing request form and tracking
|   |   |   +-- packages/       # Package browsing and management
|   |   |   +-- conflicts/      # Conflict detection display
|   |   |   +-- clash-rules/    # Clash rule management
|   |   |   +-- templates/      # Pricing template & cell mapper
|   |   |   +-- pricing-rules/  # Pricing rules management
|   |   |   +-- admin/          # User management, role assignment
|   |   |   +-- upload/         # File upload for package import
|   |   |   +-- notifications/  # Notification list and badges
|   |   +-- hooks/              # useFilterState, useLots, useExport, usePricingRequest, useClashRules
|   |   +-- api/                # API client (fetch wrappers)
|   |   +-- types/              # TypeScript interfaces matching API schemas
|   +-- package.json
|   +-- vite.config.ts
|   +-- tailwind.config.ts
|   +-- tsconfig.json
|
+-- tests/
|   +-- unit/
|   |   +-- test_lifecycle.py
|   |   +-- test_conflict.py
|   |   +-- test_normaliser.py
|   |   +-- test_filters.py
|   |   +-- test_schemas.py
|   |   +-- test_clash_validator.py
|   |   +-- test_pricing_evaluator.py
|   |   +-- test_spreadsheet_generator.py
|   +-- integration/
|   |   +-- test_api_lots.py
|   |   +-- test_api_export.py
|   |   +-- test_api_pricing.py
|   |   +-- test_api_packages.py
|   |   +-- test_api_clash_rules.py
|   |   +-- test_email_agent.py
|   |   +-- test_scraper_agent.py
|   |   +-- test_portal_agent.py
|   |   +-- test_pdf_agent.py
|   |   +-- test_package_import.py
|   |   +-- conftest.py
|   +-- e2e/
|   |   +-- test_lsi_filters.py
|   |   +-- test_lsi_export.py
|   |   +-- test_lsi_auth.py
|   |   +-- test_pricing_request.py
|   |   +-- test_clash_management.py
|   |   +-- test_role_access.py
|   +-- performance/
|       +-- test_api_load.py
|
+-- docker-compose.yml          # Local dev: PostgreSQL, Playwright
+-- Dockerfile.api              # API container
+-- Dockerfile.orchestrator     # Orchestrator + agent container
+-- Dockerfile.frontend         # Frontend build (multi-stage)
+-- pyproject.toml              # Python project config (ruff, mypy, pytest)
+-- README.md
```

---

## 10. Phased Delivery Plan

### Phase 1 — Foundation (Weeks 1-4)

| Deliverable | Agent | Reference |
|---|---|---|
| Repository scaffold, CI/CD, Docker Compose | Agent 0 | — |
| Railway project setup (API service, Frontend service, PostgreSQL plugin, Volume) | Agent 0 | §7 |
| Database schema: all 15 tables, migrations, indexes, constraints | Agent 1 | §3 |
| Seed data: estates, stages, lots, sample packages and clash rules | Agent 1 | — |
| FastAPI with full LSI API (5 endpoints, 14 query params) | Agent 2 | Addendum A |
| FastAPI with packaging API (pricing requests, clash rules, templates, packages, admin) | Agent 2 | PackagingRequirements |
| Frontend: LSI + Dashboard + Estates & Rules + Pricing Requests + Packages + Conflicts + Admin | Agent 8 | Addendum A + PackagingRequirements |
| Authentication: JWT email/password with role-based access | Agent 2 | PackagingRequirements §2 |
| **Milestone: LSI usable with seed data. Packaging workflow operational. Consultants can search/filter/export. Sales can submit pricing requests.** | | |

### Phase 2 — Packaging Engine + Ingestion Agents (Weeks 5-9)

| Deliverable | Agent | Reference |
|---|---|---|
| Spreadsheet generation engine (openpyxl, cell mapping, pricing rule injection) | Agent 9 | PackagingRequirements §6, §8, §9 |
| Clash rule validation engine (two-pass) | Agent 9 | PackagingRequirements §7 |
| Package import from Excel files | Agent 9 | PackagingRequirements §10 |
| Conflict detection across packages | Agent 9 | PackagingRequirements §7.3 |
| Email reader agent (Graph API, body + attachment parsing, LLM extraction) | Agent 3 | BRD §5.1 |
| Web scraper agent (Playwright, configurable selectors, pagination, rate limiting) | Agent 4 | BRD §5.2 |
| Portal access agent (env-stored creds, login automation, session management) | Agent 5 | BRD §5.3 |
| PDF pickup agent (Blob monitoring, pdfplumber + Doc Intelligence, archive) | Agent 6 | BRD §5.4 |
| Orchestrator: scheduling, dispatch, normalisation, conflict resolution, lifecycle engine | Agent 7 | BRD §5.5, §5.6 |
| **Milestone: End-to-end packaging workflow complete. Real estate data flowing into DB via agents.** | | |

### Phase 3 — Quality, Hardening and Launch (Weeks 10-12)

| Deliverable | Agent | Reference |
|---|---|---|
| Full test suite: 40 acceptance criteria mapped and automated | Agent 10 | §6.2 |
| Performance testing at 50,000 lots | Agent 10 | Addendum A §5.5 |
| Security testing: credential exposure, auth, role enforcement, SQL injection | Agent 10 | §4.4 |
| All documentation: ADRs, data dictionary, runbooks, user guides, traceability matrix | Agent 11 | §8 |
| LLM prompt tuning with real-world data samples | Human Tech Lead | BRD §8.3 |
| Per-site scraper/portal configuration for initial estate sources | Human Tech Lead | BRD §9 |
| Pricing template configuration for Hermitage Homes and Kingsbridge Homes | Human Tech Lead | PackagingRequirements §8 |
| UAT with consultants and sales teams | Human Tech Lead | — |
| Production deployment | Human Tech Lead + Agent 0 | — |
| **Milestone: Production go-live. Agents running on schedule. Consultants using LSI. Sales using packaging workflow.** | | |

**Total estimated duration: 12 weeks (3 months)**

---

## 11. Risk Register

| # | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| R1 | Developer website structure changes, breaking scrapers | High | High | AI-assisted fallback parsing. Monitoring to detect extraction failures. Alert on zero-record runs. |
| R2 | Portal login flow changes or blocks automation | Medium | High | Configurable login selectors. MFA detection and manual fallback flagging. Session resilience. |
| R3 | Inconsistent AI extraction from varied PDF/email formats | Medium | Medium | Confidence scoring. Low-confidence records queued for human review. Iterative prompt tuning. |
| R4 | False Unavailable markings from incomplete feeds | Medium | High | Multi-source Rule 3. Per-source status inference config. Manual override with audit trail. |
| R5 | Legal/ToS challenge from developer regarding automated access | Low | High | Per-estate legal review before automation. Polite user-agent strings. Easy source disable mechanism. |
| R6 | Credential exposure via misconfiguration | Low | Critical | Railway env vars (PoC) / Key Vault (production). Log redaction. No credentials in DB, config, or API responses. |
| R7 | Claude Code agents produce inconsistent code quality across modules | Medium | Medium | Strict linting (ruff), type checking (mypy), pre-commit hooks. Human tech lead reviews all PRs. |
| R8 | LLM extraction costs escalate with high source volume | Low | Medium | Batch extraction calls. Deterministic parsing first (CSS/XPath), LLM only as fallback. Monitor token usage. |
| R9 | Excel template format changes break spreadsheet generation | Medium | High | Cell mapping abstraction layer. Template versioning. Validation on template upload. |
| R10 | Clash rule complexity causes false positives/negatives | Low | Medium | Bidirectional enforcement. Comprehensive unit tests for edge cases. Clear error messages at submission. |
| R11 | Brand-specific logic diverges, creating maintenance burden | Medium | Medium | Clean abstraction between brand configurations. Shared base with brand-specific overrides. Template-driven rather than code-driven differences. |

---

## 12. Decision Log

| # | Decision | Status | Date | Rationale |
|---|---|---|---|---|
| ADR-001 | Python as primary language | Accepted | 2026-03-24 | LLM libs, scraping (Playwright), PDF extraction, Excel generation (openpyxl), data handling all Python-native. |
| ADR-002 | PostgreSQL over MySQL or SQL Server | Accepted | 2026-03-24 | Superior jsonb support (for template mappings, form data, scraping config), better indexing options. Railway plugin for PoC, Azure Flexible Server for production. |
| ADR-003 | Railway for PoC, Azure for production | Accepted | 2026-04-05 | Railway provides rapid deployment, low cost ($21-63/month), and simple configuration for PoC validation. Azure deferred to production for enterprise features (HA, VNet, Key Vault, CDN). |
| ADR-004 | FastAPI over Django or Flask | Accepted | 2026-03-24 | Async-native, auto-generated OpenAPI spec, Pydantic validation matches query parameter and form data specs precisely. |
| ADR-005 | Microsoft Graph API or IMAP for email access | Accepted | 2026-03-24 | Graph API for M365 mailboxes (production). IMAP as fallback for PoC or non-M365 providers. |
| ADR-006 | LangGraph for orchestration over Celery or raw cron | Proposed | 2026-03-24 | Structured agent state management, conditional routing, retry patterns. Evaluate in Phase 2. Fallback: APScheduler + custom dispatcher. |
| ADR-007 | React + Vite + shadcn/ui for frontend | Accepted | 2026-03-24 | TanStack Table for data tables. shadcn/ui provides accessible, customisable components. Supports both LSI and packaging UI. |
| ADR-008 | Bicep for Azure IaC (production) | Deferred | 2026-04-05 | Azure-native IaC deferred until production migration. PoC uses Railway configuration (railway.toml + dashboard). |
| ADR-009 | Claude API (Sonnet) as primary LLM for extraction | Proposed | 2026-03-24 | Strong structured extraction capabilities. JSON mode with schema validation. Model-swappable prompts. |
| ADR-010 | Documentation as code (Markdown in repo) | Accepted | 2026-03-24 | Version-controlled, diffable, deploys with code. |
| ADR-011 | Tesseract OCR for PoC, Azure Document Intelligence for production | Accepted | 2026-04-05 | Tesseract (open-source, in-container) for PoC to avoid cloud OCR costs. Upgrade to Azure Document Intelligence for production if accuracy requires it. |
| ADR-012 | openpyxl for Excel spreadsheet generation | Accepted | 2026-03-27 | Supports .xlsx and .xlsm formats. Cell-level read/write, data validation extraction, formula preservation. Required for pricing template workflow. |
| ADR-013 | Email/password auth with role-based access for packaging system | Accepted | 2026-03-27 | Packaging system requires granular roles (Admin, Pricing, Sales, Requester) beyond SSO. user_roles table for privilege escalation prevention. |
| ADR-014 | Client-side conflict detection | Accepted | 2026-03-27 | Clash rules and packages fetched to client for real-time conflict detection. Avoids server round-trips for every package change. Feasible at current data volumes. |
| ADR-015 | Rename project from LAAS to House and Land Packager | Accepted | 2026-04-05 | Project scope expanded beyond data aggregation to include full packaging, pricing, and clash management workflow. |
| ADR-016 | Railway for PoC deployment | Accepted | 2026-04-05 | Single API service + PostgreSQL plugin + Railway Volume. ~$21-63/month vs ~$250-680/month on Azure. Production migration triggered when: (a) concurrent users exceed Railway limits, (b) enterprise SSO required, (c) compliance mandates private networking/Key Vault. |
| ADR-017 | Self-managed JWT auth for PoC | Accepted | 2026-04-05 | bcrypt password hashing + JWT tokens + user_roles table. Avoids third-party auth service cost. Migrate to Entra ID for production SSO/MFA. |
| ADR-018 | GitHub personal account for repository | Accepted | 2026-04-05 | Repository: github.com/[user]/house-and-land-packager. Migrate to org account if team grows. |

---

## 13. Getting Started

### 13.1 Prerequisites

```bash
# Python
python --version   # >= 3.12

# Node.js (for frontend)
node --version     # >= 20 LTS

# Docker (for local PostgreSQL)
docker --version   # >= 24

# Railway CLI (for deployment)
railway --version  # Install: npm install -g @railway/cli

# Playwright
playwright install chromium
```

### 13.2 Local Environment Bootstrap

```bash
# Clone repository
git clone https://github.com/<your-username>/house-and-land-packager.git
cd house-and-land-packager

# Python setup
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# Start local infrastructure
docker compose up -d   # PostgreSQL (5432)

# Run database migrations
alembic upgrade head

# Seed development data
python -m hlp.seeds.dev_seed

# Start the API
uvicorn hlp.api.main:app --reload --port 8000

# Start the frontend (separate terminal)
cd frontend
npm install
npm run dev   # Vite dev server on port 5173

# Run tests
pytest tests/unit/
pytest tests/integration/   # requires Docker services running
```

### 13.3 Railway Deployment

```bash
# Login to Railway
railway login

# Link to project (first time)
railway link

# Deploy (or push to GitHub main branch for auto-deploy)
railway up

# View logs
railway logs

# Open deployed app
railway open
```

---

## 14. Corrections from Previous Versions

### v2.0 → v3.0 (5 April 2026)

| Change | Detail |
|---|---|
| Project renamed | "Land Availability Automation System (LAAS)" → "House and Land Packager" |
| Scope expanded | Added full house & land package pricing, clash management, and Excel template generation (from PackagingRequirements_Document.docx) |
| Data model expanded | 6 entities → 15 tables (added regions, estate_stages, stage_lots, house_packages, clash_rules, pricing_requests, pricing_templates, pricing rules, profiles, user_roles, notifications, estate_documents) |
| Lot entity enriched | Added corner_block, orientation, side/rear easement, street_name, build_price, package_price, substation, design, facade, brand fields |
| New agent added | Agent 9 (Packaging Engine) for spreadsheet generation, clash validation, pricing rule evaluation |
| Frontend scope expanded | LSI-only → full application with Dashboard, Estates & Rules, Pricing Requests, Packages, Conflicts, Admin, Upload, Notifications |
| User roles added | Admin, Pricing, Sales, Requester roles for packaging system access control |
| Brand-specific logic | Hermitage Homes and Kingsbridge Homes with different templates, fields, and data validations |
| Acceptance criteria expanded | 26 criteria → 40 criteria (14 new packaging system criteria) |
| New risks added | R9 (template format changes), R10 (clash rule complexity), R11 (brand logic divergence) |
| New ADRs | ADR-012 (openpyxl), ADR-013 (email/password auth + roles), ADR-014 (client-side conflict detection), ADR-015 (project rename) |
| Deployment target | Azure (all environments) → Railway (PoC), Azure deferred to production |
| Cost reduction | $250-680/month (Azure) → $21-63/month (Railway PoC) |
| File storage | Azure Blob Storage → Railway Volume |
| Secrets management | Azure Key Vault → Railway environment variables |
| Authentication | Entra ID + email/password → Self-managed JWT + email/password |
| OCR | Azure Document Intelligence → Tesseract OCR (open source) |
| Monitoring | Azure App Insights → structlog + Railway metrics |
| IaC | Bicep → railway.toml (Bicep deferred to production) |
| Python package renamed | `laas` → `hlp` |
| Repository renamed | `laas/` → `house-and-land-packager/` |
| GitHub repo | Created at github.com/[user]/house-and-land-packager |

### v1.0 → v2.0 (24 March 2026)

| Previous Assumption | Actual BRD Requirement |
|---|---|
| System is an internal estate data management tool | System is an AI-powered external data **aggregation** platform |
| 13 entities including PriceList, PriceHistory, Rebate, RebateRule, RebateAuditLog, SiteCost, SiteCostCategory | 6 entities: Developer, Estate, Lot, StatusHistory, IngestionLog, Configuration |
| Rebate management module with agent extraction | No rebate concept exists in the BRD |
| Pricing engine with escalation rules and margin calculation | System scrapes prices from external sources |
| Site cost tracking and allocation | Not in scope |
| Node.js / .NET runtime | Python is the recommended runtime |
| Azure SQL Database | PostgreSQL |
| 8-10 person human team | Claude Code agent team with human tech lead |
| 24-week delivery timeline | 12-week delivery |

---

*This document should be committed to the repository root as `PROJECT_SETUP.md` and used as the primary reference for all Claude Code agent task assignments.*

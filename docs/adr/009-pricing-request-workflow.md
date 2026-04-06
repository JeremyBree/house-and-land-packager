# ADR-009: Pricing Request Workflow

**Status:** Accepted  
**Date:** 2026-04-05  
**Deciders:** Engineering team  

## Context

The core business feature of the House and Land Packager is the pricing request workflow. Sales staff need to submit requests that include estate, stage, brand, and lot-level details. The system must validate clash rules, generate a pre-filled Excel spreadsheet from brand-specific templates, and support a fulfilment lifecycle where pricing team members upload completed sheets that are then imported as packages.

## Decision

We implement a submit-generate-fulfil-notify lifecycle:

1. **Submit:** Sales submits a `PricingRequestCreate` payload. The system validates brand-specific requirements (Hermitage requires BDM + wholesale group), runs two-pass clash validation (within-request and against existing packages), creates the request record, and generates a pre-filled Excel spreadsheet from the brand template using openpyxl.

2. **Generate:** The `SpreadsheetService` loads the brand template from storage, injects header data into mapped cells, lot data starting at the configured row, and applicable pricing rules (filtered by condition evaluation). The generated workbook is stored and linked to the request.

3. **Fulfil:** Admin/pricing users download the generated sheet, fill in pricing data, and upload the completed sheet. The system extracts package data from the completed sheet and creates `HousePackage` records. The request is marked as Completed.

4. **Notify:** On completion, an in-app notification is created for the original requester.

5. **Resubmit:** Completed requests can be cloned by returning the stored `form_data` as a pre-filled create payload.

## Consequences

- Clash violations block submission with a 409 response including detailed violation information
- Role-based access: sales/requester users see only their own requests; admin/pricing see all
- The JSONB `form_data` column stores the complete submission payload, enabling resubmit without data loss
- Spreadsheet generation depends on a template being uploaded for the brand; `TemplateNotFoundError` is raised otherwise
- Package extraction from completed sheets is best-effort: rows with missing design or facade are skipped

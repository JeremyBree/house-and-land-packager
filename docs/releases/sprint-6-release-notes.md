# Sprint 6 Release Notes

**Release Date:** 2026-04-05  
**Sprint Goal:** Core pricing request workflow

## What's New

### Pricing Request Workflow
- **Submit pricing requests** with estate, stage, brand, toggles, and per-lot entries
- **Two-pass clash validation** blocks submissions with design+facade conflicts (within request and against existing packages)
- **Auto-generated Excel spreadsheet** from brand template with injected headers, lot data, and pricing rules
- **Fulfilment workflow:** pricing team downloads generated sheet, fills pricing data, uploads completed sheet
- **Package extraction:** completed sheets are parsed and HousePackage records are created automatically
- **Request lifecycle:** Pending -> In Progress -> Completed
- **Resubmit:** clone completed requests as new drafts with pre-filled form data

### In-App Notifications
- Requesters are notified when their pricing requests are completed
- Notification bell in header with unread count badge and recent notification dropdown
- Full notifications page with pagination and mark-read controls

### Brand-Specific Logic
- Hermitage Homes: requires BDM and Wholesale Group, supports Garage Side per lot
- Kingsbridge Homes: supports Custom House Design toggle per lot

### Role-Based Access
- Sales/requester users see only their own requests
- Admin/pricing users see all requests and can fulfil them
- Delete permissions: owners can delete own, admin/pricing can delete any

## Frontend
- PricingRequestsPage with status and brand filters
- PricingRequestFormPage with dynamic brand-specific fields and clash error display
- PricingRequestDetailPage with download, upload, resubmit, and delete actions
- NotificationBell component in header
- NotificationsPage for full notification management
- Pricing Requests promoted from placeholder to active sidebar link

## API Endpoints Added
- 8 pricing request endpoints (submit, list, detail, download, fulfil, download-completed, resubmit, delete)
- 4 notification endpoints (list, unread-count, mark-read, mark-all-read)

## Tests
- ~30 new tests covering submission, clash violations, fulfilment, role filtering, notifications, and spreadsheet generation

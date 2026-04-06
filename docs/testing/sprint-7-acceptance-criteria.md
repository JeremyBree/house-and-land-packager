# Sprint 7 Acceptance Criteria

## Dashboard
- [ ] Dashboard loads for any authenticated user and displays metric cards
- [ ] Total estates, lots, packages, conflicts, and pending requests counts are accurate
- [ ] Lot status breakdown percentages sum to 100% (or close due to rounding)
- [ ] Recent requests shows the last 5 pricing requests with correct status badges
- [ ] Quick action links navigate to the correct pages

## Configurations
- [ ] Admin can list, create, update, and delete ingestion configurations
- [ ] Credentials reference is masked as "[configured]" in all API responses
- [ ] Enable/disable toggle works without opening the edit dialog
- [ ] Filtering by type and enabled status returns correct results
- [ ] Non-admin users receive 403 Forbidden

## Ingestion Logs
- [ ] Admin can view paginated ingestion logs with correct totals
- [ ] Detail dialog shows error information for failed runs
- [ ] Filtering by agent type and status works correctly
- [ ] Non-admin users receive 403 Forbidden

## Navigation
- [ ] Sidebar shows Configurations and Ingestion Logs under Admin section
- [ ] All sidebar links are active (no "coming soon" placeholders)

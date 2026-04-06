# Sprint 7 Release Notes — Final PoC Release

**Date**: 2026-04-05
**Version**: 0.7.0 (PoC Complete)

## Summary

Sprint 7 completes the House and Land Packager proof-of-concept. This final sprint delivers the live dashboard, ingestion configuration management, ingestion log viewing, and overall polish.

## What's New

### Dashboard with Live Data
- Real-time metric cards: estates, lots, packages, active conflicts, pending requests
- Lot status breakdown with visual progress bars
- Recent pricing requests feed with status badges
- Quick action shortcuts for common workflows

### Ingestion Configuration Management (Admin)
- Full CRUD for data source configurations (email, website, portal, PDF folder)
- Type-specific icons and labels
- Enable/disable toggle without opening edit dialog
- Credential masking in API responses ("[configured]" instead of raw env var names)
- Filtering by type and enabled status

### Ingestion Logs Viewer (Admin)
- Paginated log history of all agent runs
- Status badges: success (green), partial (amber), failed (red)
- Record count breakdown: found / created / updated / deactivated
- Detail dialog with full error information for debugging failed runs
- Filtering by agent type and status

### Navigation Polish
- All sidebar links are now active and functional
- Admin submenu expanded with Configurations and Ingestion Logs

## Complete PoC Feature Summary (Sprints 1-7)

| Sprint | Features |
|--------|----------|
| 1 | Auth, users, estates, regions, developers |
| 2 | Stages, lots, documents, file storage, status lifecycle |
| 3 | Land Search Interface, filter presets, CSV/XLSX export |
| 4 | Clash rules, packages, conflict detection |
| 5 | Pricing templates, pricing rules (global + stage), rule categories |
| 6 | Pricing requests, spreadsheet generation, notifications |
| 7 | Dashboard, ingestion configs, ingestion logs, polish |

## Technical Details
- **Backend routes**: 112
- **Integration tests**: 368 passing
- **Frontend**: Clean production build
- **API lint**: All new Sprint 7 code passes ruff checks

## Known Limitations (PoC)
- Ingestion agents are not yet wired to real data sources (configurations are managed but agents run as stubs)
- No WebSocket/SSE for real-time dashboard updates (polling via React Query)
- Single-service deployment (API + scheduler in one process)
- SQLite test database (production uses PostgreSQL)

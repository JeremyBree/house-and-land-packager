# Sprint 7: Dashboard and Admin Guide

## Dashboard

The dashboard is the first screen users see after login. It provides a real-time overview of the system:

### Metric Cards
- **Total Estates** — count of all registered estates (links to estate list)
- **Total Lots** — count of all lots across all stages (links to Land Search)
- **Active Conflicts** — count of clash violations detected across all estates (links to conflicts page). Shown in red when conflicts exist, green when clean.
- **Pending Requests** — count of pricing requests awaiting processing (links to pricing requests list)

### Lot Status Breakdown
A horizontal bar chart showing the distribution of lots by status:
- Available (green)
- Hold (yellow)
- Deposit Taken (blue)
- Sold (purple)
- Unavailable (grey)

Each bar shows the count and percentage of total lots.

### Quick Actions
Shortcut buttons for common tasks:
- New Pricing Request
- Search Lots
- View Conflicts
- Browse Packages

### Recent Pricing Requests
The last 5 pricing submissions with estate name, stage, brand, lot count, and status badge (Pending/In Progress/Completed).

## Ingestion Configurations (Admin only)

Navigate to Admin > Configurations in the sidebar.

### Managing Configurations
Each configuration represents a data source for the ingestion agents:
- **Email Account** — monitors an inbox for lot data emails
- **Website** — scrapes a developer's lot listing page
- **Portal** — connects to a developer portal API
- **PDF Folder** — watches a folder for new PDF price lists

### Configuration Table
Shows all configurations with:
- Label and type (with type-specific icon)
- URL or path
- Run schedule (cron expression)
- Enabled toggle (click to enable/disable without editing)
- Priority rank (lower = higher priority)
- Edit and delete actions

### Creating/Editing
Click "Add Configuration" or the edit icon to open the form:
1. Select the source type
2. Enter a descriptive label
3. Provide the URL or folder path
4. Set an optional cron schedule (e.g., `0 */6 * * *` for every 6 hours)
5. Set priority rank if multiple sources feed the same estate
6. Add notes for documentation

### Security
Credential references (environment variable names) are never exposed in the UI — they show as "[configured]" when set.

## Ingestion Logs (Admin only)

Navigate to Admin > Ingestion Logs in the sidebar.

### Viewing Logs
The log table shows the history of all agent runs with:
- Timestamp
- Agent type (Email, Scraper, Portal, PDF)
- Source identifier
- Record counts (found / created / updated / deactivated)
- Status badge (green=success, yellow=partial, red=failed)

### Filtering
Use the dropdown filters to narrow by:
- Agent type
- Status

### Error Details
Click "Detail" on any log entry to see full information. Failed runs include the error message and stack trace for debugging.

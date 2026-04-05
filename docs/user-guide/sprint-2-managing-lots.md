# Managing Stages, Lots, and Documents — Sprint 2

This guide walks through the features shipped in Sprint 2: estate
stages, stage lots (individually or in bulk), lot status transitions,
status history, and estate documents.

It assumes you are already logged in (see the Sprint 1 admin
quickstart).

## Stages

Every estate contains one or more **stages** — release-based
subdivisions that group lots for pricing and marketing.

### Add a stage to an estate (Admin)

1. Sidebar → **Estates**.
2. Click the estate to open its detail page.
3. Under **Stages**, click **New stage**.
4. Fill in:
   - **Name** (required, e.g. `Stage 1A`).
   - **Lot count** — the planned lot count (informational).
   - **Status** — `Active`, `Upcoming`, or `Completed`. Defaults to
     `Active`.
   - **Release date** — optional.
5. Click **Save**.

### Edit or delete a stage (Admin)

- Click a stage to open its detail page, then **Edit** to change
  fields.
- **Delete** removes the stage **and all its lots and their status
  history**. Deletes are hard and cascading — act carefully.

## Lots

Each stage contains a list of **lots**. Sprint 2 supports three ways
to add lots:

### Add a single lot (Admin)

1. Open the stage detail page.
2. Click **New lot**.
3. Fill in at minimum the **Lot number** (unique within the stage).
4. Optionally fill in frontage, depth, size, orientation, easements,
   street name, prices, and title date.
5. Click **Save**. New lots start with status **Available** and
   source **Manual**.

### Add multiple lots at once — Bulk (Admin)

Useful when you're pasting in a small batch from a spreadsheet.

1. Stage detail page → **Bulk add**.
2. Paste or type in a JSON array of lot objects.
3. Click **Save**. The response shows how many lots were created and
   how many were skipped (duplicates).

### Add lots from a CSV file (Admin)

Preferred for developer price lists of more than a handful of lots.

1. Stage detail page → **Upload CSV**.
2. Select your CSV file and click **Upload**.
3. The result summary shows **created / skipped / errors**.

See **`docs/operations/runbooks/sprint-2-csv-upload-guide.md`** for
the supported columns, value formats, size limits, and troubleshooting.

### Edit a lot (Admin)

Click the lot row in the stage detail view. Change any field **except
status** and click **Save**. Status is changed through the dedicated
transition workflow, below.

### Delete a lot (Admin)

Open the lot detail panel and click **Delete**. This removes the lot
and its entire status history. Undo is not supported.

## Lot Status

Every lot has one of five statuses:

| Status | Meaning |
|---|---|
| `Available` | Open for sale |
| `Unavailable` | Explicitly off-market (price review, developer hold) |
| `Hold` | Held for a specific agent / buyer |
| `Deposit Taken` | Buyer has paid deposit |
| `Sold` | Contract exchanged |

### Transition a lot's status (Admin or Pricing)

1. Open the lot detail panel.
2. Click **Change status**.
3. Pick the new status from the dropdown.
4. Enter a **reason** (required, up to 500 chars). Examples:
   - `Held for agent Jane until Friday`
   - `Confirmed by developer — no change this week`
   - `Contract exchanged today`
5. Click **Save**.

Every transition:

- Writes a new row to **status history** recording the previous
  status, new status, timestamp, your email, and the reason.
- Updates the lot's **last confirmed date** to the transition
  timestamp.
- Is recorded **even if the new status equals the current status** —
  this is how we capture weekly "re-confirmation" events.

### View status history

On the lot detail panel, expand **Status history** to see every
transition, most recent first. Each row shows: timestamp, previous
→ new status, triggering agent (`manual:{your-email}` for user
actions), and the reason.

## Estate Documents

Upload developer price lists, estate plans, and marketing collateral
against an estate (or against a specific stage within it).

### Upload a document (Admin)

1. Estate detail page → **Documents** tab.
2. Click **Upload document**.
3. Choose the file. Supported: PDF, DOC, DOCX, PNG, JPG, JPEG, up to
   **10 MB**.
4. Optionally pick a **stage** to scope the document to.
5. Add an optional **description**.
6. Click **Upload**.

The document appears in the list immediately with a **Download** link.

### Download a document

Any authenticated user can click the download link in the document
list. The browser uses the original filename.

### Delete a document (Admin)

Click the trash icon next to the document. This deletes both the
database row and the underlying file from storage.

## Role Permissions — Sprint 2

| Action | admin | pricing | sales | requester |
|---|:---:|:---:|:---:|:---:|
| List estates, stages, lots, documents | yes | yes | yes | yes |
| View lot status history | yes | yes | yes | yes |
| Create / edit / delete stages | yes | — | — | — |
| Create / edit / delete lots | yes | — | — | — |
| Bulk create / CSV upload lots | yes | — | — | — |
| **Transition lot status** | **yes** | **yes** | — | — |
| Upload / delete estate documents | yes | — | — | — |
| Download documents | yes | yes | yes | yes |

## Coming in Sprint 3

- **Land Search Interface (LSI)** — search and filter all active lots
  across every estate.
- **Export** — CSV export of the LSI result set.

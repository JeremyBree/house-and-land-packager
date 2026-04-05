# Runbook: CSV Upload for Stage Lots

This runbook is for operators and admins who need to bulk-load lots
into a stage via the `POST /api/stages/{stage_id}/lots/upload-csv`
endpoint. The frontend's "Upload CSV" button on the Stage detail page
is a thin wrapper over the same endpoint.

## File Format

- **Encoding**: UTF-8 (BOM is accepted and stripped).
- **Header row**: required. Column names are **case-insensitive** and
  whitespace-trimmed.
- **Separator**: comma.
- **Quoting**: standard CSV quoting (double-quote strings containing
  commas).

## Supported Columns

| Column | Required | Type | Notes |
|---|---|---|---|
| `lot_number` | yes | string (1-50 chars) | unique within a stage |
| `frontage` | no | decimal (2dp) | metres |
| `depth` | no | decimal (2dp) | metres |
| `size_sqm` | no | decimal (2dp) | square metres |
| `corner_block` | no | boolean | default `false` |
| `orientation` | no | string (max 20) | e.g. `N`, `NE`, `S` |
| `side_easement` | no | decimal (2dp) | metres |
| `rear_easement` | no | decimal (2dp) | metres |
| `street_name` | no | string (max 255) | |
| `land_price` | no | decimal (2dp) | AUD |
| `build_price` | no | decimal (2dp) | AUD |
| `package_price` | no | decimal (2dp) | AUD |
| `title_date` | no | date | `YYYY-MM-DD` |

Unknown columns are silently ignored. Empty cells for optional
columns are treated as "not provided" (NULL in the DB).

## Accepted Value Formats

- **Booleans**: `yes` / `no` / `true` / `false` / `1` / `0` /
  `y` / `n` / `t` / `f` (all case-insensitive). Blank is treated as
  `false`.
- **Decimals**: `385000`, `385000.00`, `12.5` all accepted. Two decimal
  places is the convention for money and dimensions. The backend
  stores `Decimal`, so no float rounding.
- **Dates**: `YYYY-MM-DD` only (e.g. `2026-02-01`).

## Example CSV

```csv
lot_number,frontage,depth,size_sqm,corner_block,orientation,street_name,land_price,build_price,package_price,title_date
L101,12.50,32.00,400.00,no,N,Aurora Blvd,385000.00,275000.00,660000.00,2026-02-01
L102,14.00,32.00,448.00,yes,NE,Aurora Blvd,410000.00,290000.00,700000.00,2026-02-01
L103,12.50,34.00,425.00,no,S,Horizon Way,395000.00,278000.00,673000.00,2026-03-01
```

## Behaviour

- The CSV is parsed **all-or-nothing**. If any row has an invalid
  boolean, decimal, or date, the entire upload is rejected with a
  400 `invalid_csv` error and no lots are created.
- Once parsing succeeds, lots are inserted one at a time:
  - Duplicates **within the uploaded CSV** (same `lot_number`
    repeated) are **skipped** — the first occurrence is created, the
    rest are counted as `skipped`.
  - Lots whose `lot_number` already exists in the target stage are
    **skipped** — not errored, not overwritten.
- The response is a `CsvUploadResult`:
  ```json
  { "created": 18, "skipped": 2, "errors": [] }
  ```
- Completely empty rows (every cell blank) are ignored silently.

## Recommended Limits

- Keep uploads **under 5,000 rows** per file for reasonable
  performance. Larger files are parsed in a single request and commit
  in one transaction, which holds a database connection for the
  duration.
- For bigger loads, split the file into chunks of ~2,000 rows.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `CSV is missing required column 'lot_number'` | Header typo or wrong file | Confirm the first row has a `lot_number` column. |
| `Row N: 'lot_number' is required` | Empty `lot_number` cell on a non-empty row | Fill in or delete the row. |
| `Row N: invalid boolean for 'corner_block': 'maybe'` | Unrecognised boolean value | Use `yes`/`no`/`true`/`false`/`1`/`0`/`y`/`n`. |
| `Row N: invalid decimal for 'land_price': '$385,000'` | Currency symbols or thousands separators in a decimal column | Strip the `$` and `,`; supply bare digits with a decimal point. |
| `Row N: invalid date for 'title_date' (expected YYYY-MM-DD): '01/02/2026'` | Wrong date format | Convert to ISO-8601 `YYYY-MM-DD`. |
| `File is not valid UTF-8` | CSV saved with a non-UTF-8 encoding | Re-save as UTF-8 in Excel/LibreOffice (CSV UTF-8). |
| Response shows `skipped > 0` but you expected all new | Lot numbers already exist in the stage | Compare your CSV against `GET /api/stages/{id}/lots`; rename or omit duplicates. |
| 413 / request-too-large | File exceeds Railway's default upload limit | Split the CSV into smaller chunks. |

## Verifying the Result

After a successful upload, verify from the CLI:

```bash
curl "https://house-and-land-packager-production.up.railway.app/api/stages/3/lots?size=200" \
  -H "Authorization: Bearer $TOKEN" | jq '.total'
```

Or open the Stage detail page in the UI — the lot list reflects the
insert immediately.

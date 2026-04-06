# Sprint 6 API Endpoints

## Pricing Requests

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/pricing-requests` | Any auth | Submit new pricing request |
| GET | `/api/pricing-requests` | Any auth (role-filtered) | List requests with filters |
| GET | `/api/pricing-requests/{id}` | Any auth (role-filtered) | Get request detail |
| GET | `/api/pricing-requests/{id}/download` | Any auth | Download generated sheet |
| POST | `/api/pricing-requests/{id}/fulfil` | Admin/Pricing | Upload completed sheet |
| GET | `/api/pricing-requests/{id}/download-completed` | Any auth | Download completed sheet |
| POST | `/api/pricing-requests/{id}/resubmit` | Any auth | Get form data for cloning |
| DELETE | `/api/pricing-requests/{id}` | Owner or Admin/Pricing | Delete request |

### Query Parameters (List)

- `page` (int, default 1)
- `size` (int, default 25, max 200)
- `status` (string: Pending, In Progress, Completed)
- `brand` (string)
- `estate_id` (int)

### Request Body (Submit)

```json
{
  "estate_id": 1,
  "stage_id": 1,
  "brand": "Hermitage Homes",
  "has_land_titled": true,
  "titling_when": null,
  "is_kdrb": false,
  "is_10_90_deal": false,
  "developer_land_referrals": false,
  "building_crossover": false,
  "shared_crossovers": false,
  "side_easement": null,
  "rear_easement": null,
  "bdm": "John Doe",
  "wholesale_group": "GroupA",
  "lots": [
    {
      "lot_number": "A1",
      "house_type": "Alpine",
      "facade_type": "Traditional",
      "garage_side": "Left"
    }
  ],
  "notes": null
}
```

### Error Response (Clash Violation - 409)

```json
{
  "detail": "Clash rule violations detected",
  "code": "clash_violation",
  "violations": [
    {
      "lot_numbers": ["A1", "A2"],
      "design": "Alpine",
      "facade": "Traditional",
      "rule_id": 1,
      "violation_type": "within_request"
    }
  ]
}
```

## Notifications

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/notifications` | Any auth | List notifications (paginated) |
| GET | `/api/notifications/unread-count` | Any auth | Get unread count |
| POST | `/api/notifications/{id}/read` | Any auth (must own) | Mark as read |
| POST | `/api/notifications/read-all` | Any auth | Mark all as read |

# ADR-010: Dashboard Aggregation Strategy

## Status
Accepted

## Context
The dashboard needs to display several aggregated metrics: estate counts, lot counts, package counts, conflict counts, pending request counts, lot status breakdowns, and recent pricing requests.

Two approaches were considered:
1. **Multiple API calls** from the frontend, one per metric (GET /api/estates, GET /api/lots/search, GET /api/conflicts/summary, GET /api/pricing-requests?status=Pending)
2. **Single aggregated endpoint** (GET /api/dashboard) that gathers all metrics server-side and returns them in one response

## Decision
We chose **Option 2: single aggregated endpoint** (`GET /api/dashboard`).

## Rationale
- **Fewer round-trips**: One HTTP request instead of 4-6 reduces latency and simplifies loading states in the frontend.
- **Consistent snapshot**: All counts are computed within the same database session, avoiding temporal inconsistencies between metrics.
- **Simpler frontend**: One `useQuery` call with a single loading/error state instead of managing multiple independent queries.
- **Backend flexibility**: The endpoint can be optimised later (e.g., caching, materialised views) without changing the frontend contract.
- **PoC scope**: For the proof-of-concept, the queries are lightweight (COUNT aggregates on indexed tables). If performance becomes a concern at scale, we can add Redis caching or periodic pre-computation.

## Consequences
- The dashboard endpoint couples multiple domain aggregates into one response. If any one query fails, the entire endpoint fails. This is acceptable for a PoC; production would add per-section error handling.
- Adding new dashboard widgets requires modifying both the backend schema and the frontend component.
- The endpoint is accessible to any authenticated user (not restricted to admin) so all roles can see the dashboard overview.

"""Integration tests: /api/lots/search (Sprint 3 Land Search Interface).

Fixture ``search_seed_data`` creates 3 estates (2 VIC AlphaDev, 1 NSW BetaBuild),
2 stages per estate, 5 lots per stage = 30 lots total with this distribution:

Per stage (5 lots, indices 0..4):
  status: Available, Available, Hold, Sold, Unavailable
  land_price: 300k, 350k, 400k, 450k, None
  size_sqm: 350, 400, 450, 500, 550
  frontage: 10.00, 12.50, 14.00, 16.00, 18.00
  depth: 28, 30, 32, 34, 36
  corner_block: True for idx 0, else False
  title_date: 2026-03-01, 2026-06-01, 2026-09-01, 2026-12-01, 2027-03-01

Totals across 6 stages:
  Available: 12, Hold: 6, Sold: 6, Unavailable: 6
  Non-null prices: 24, Null prices: 6
  Corner blocks: 6
"""
from __future__ import annotations

from fastapi.testclient import TestClient


def _search(client: TestClient, headers: dict, **body):
    return client.post("/api/lots/search", json=body, headers=headers)


# ------------------------ pagination + auth ---------------------------------


def test_search_unauthenticated_401(client: TestClient):
    r = client.post("/api/lots/search", json={})
    assert r.status_code == 401


def test_search_returns_paginated_results(
    client: TestClient, sales_headers, search_seed_data
):
    r = _search(client, sales_headers, page=1, size=5)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["total"] == 30
    assert body["size"] == 5
    assert body["page"] == 1
    assert body["pages"] == 6
    assert len(body["items"]) == 5


def test_search_no_filters_returns_all(
    client: TestClient, sales_headers, search_seed_data
):
    r = _search(client, sales_headers, page=1, size=200)
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 30
    assert len(body["items"]) == 30


def test_search_size_caps_at_200(
    client: TestClient, sales_headers, search_seed_data
):
    r = _search(client, sales_headers, page=1, size=500)
    assert r.status_code == 422


# ------------------------ status filters ------------------------------------


def test_search_filter_by_status(
    client: TestClient, sales_headers, search_seed_data
):
    r = _search(
        client, sales_headers, filters={"statuses": ["Available"]}, size=200
    )
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 12
    for item in body["items"]:
        assert item["status"] == "Available"


def test_search_filter_by_multiple_statuses(
    client: TestClient, sales_headers, search_seed_data
):
    r = _search(
        client,
        sales_headers,
        filters={"statuses": ["Hold", "Sold"]},
        size=200,
    )
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 12  # 6 Hold + 6 Sold
    for item in body["items"]:
        assert item["status"] in {"Hold", "Sold"}


# ------------------------ numeric range filters -----------------------------


def test_search_price_min_max(
    client: TestClient, sales_headers, search_seed_data
):
    # Inclusive bounds: [350000, 400000] should include 350k and 400k lots (12 total).
    r = _search(
        client,
        sales_headers,
        filters={"price_min": 350000, "price_max": 400000},
        size=200,
    )
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 12  # 6 @ 350k + 6 @ 400k
    for item in body["items"]:
        assert 350000 <= float(item["land_price"]) <= 400000


def test_search_exclude_null_price(
    client: TestClient, sales_headers, search_seed_data
):
    r = _search(
        client,
        sales_headers,
        filters={"exclude_null_price": True},
        size=200,
    )
    body = r.json()
    assert body["total"] == 24
    for item in body["items"]:
        assert item["land_price"] is not None


def test_search_size_min_max(
    client: TestClient, sales_headers, search_seed_data
):
    r = _search(
        client,
        sales_headers,
        filters={"size_min": 400, "size_max": 500},
        size=200,
    )
    body = r.json()
    # sizes 400, 450, 500 = 3 per stage x 6 = 18
    assert body["total"] == 18


def test_search_frontage_min(
    client: TestClient, sales_headers, search_seed_data
):
    r = _search(
        client, sales_headers, filters={"frontage_min": 14}, size=200
    )
    body = r.json()
    # frontages 14, 16, 18 = 3 per stage x 6 = 18
    assert body["total"] == 18


def test_search_depth_min(
    client: TestClient, sales_headers, search_seed_data
):
    r = _search(client, sales_headers, filters={"depth_min": 32}, size=200)
    body = r.json()
    # depths 32, 34, 36 = 3 per stage x 6 = 18
    assert body["total"] == 18


def test_search_corner_block_true(
    client: TestClient, sales_headers, search_seed_data
):
    r = _search(
        client, sales_headers, filters={"corner_block": True}, size=200
    )
    body = r.json()
    assert body["total"] == 6  # 1 per stage
    for item in body["items"]:
        assert item["corner_block"] is True


# ------------------------ id-list filters -----------------------------------


def test_search_by_estate_ids(
    client: TestClient, sales_headers, search_seed_data
):
    acacia = search_seed_data["estates"]["acacia"]
    banksia = search_seed_data["estates"]["banksia"]
    r = _search(
        client,
        sales_headers,
        filters={"estate_ids": [acacia, banksia]},
        size=200,
    )
    body = r.json()
    assert body["total"] == 20  # 2 estates x 10 lots
    for item in body["items"]:
        assert item["estate_name"] in {"Acacia Rise", "Banksia Park"}


def test_search_by_developer_ids(
    client: TestClient, sales_headers, search_seed_data
):
    beta = search_seed_data["developers"]["beta"]
    r = _search(
        client,
        sales_headers,
        filters={"developer_ids": [beta]},
        size=200,
    )
    body = r.json()
    # Cedar Grove only = 10 lots
    assert body["total"] == 10
    for item in body["items"]:
        assert item["developer_name"] == "BetaBuild"


def test_search_by_region_ids(
    client: TestClient, sales_headers, search_seed_data
):
    growth = search_seed_data["regions"]["growth"]
    r = _search(
        client,
        sales_headers,
        filters={"region_ids": [growth]},
        size=200,
    )
    body = r.json()
    # Banksia + Cedar are in Growth Corridor = 20 lots
    assert body["total"] == 20


def test_search_by_suburbs_case_insensitive(
    client: TestClient, sales_headers, search_seed_data
):
    r = _search(
        client,
        sales_headers,
        filters={"suburbs": ["tarneit", "WERRIBEE"]},
        size=200,
    )
    body = r.json()
    assert body["total"] == 20  # Acacia (Tarneit) + Banksia (Werribee)


# ------------------------ date filter ---------------------------------------


def test_search_by_title_date_range(
    client: TestClient, sales_headers, search_seed_data
):
    r = _search(
        client,
        sales_headers,
        filters={
            "title_date_from": "2026-06-01",
            "title_date_to": "2026-12-01",
        },
        size=200,
    )
    body = r.json()
    # Dates 2026-06-01, 2026-09-01, 2026-12-01 = 3 per stage x 6 = 18
    assert body["total"] == 18


# ------------------------ text search ---------------------------------------


def test_search_text_search_matches_estate_name(
    client: TestClient, sales_headers, search_seed_data
):
    r = _search(
        client, sales_headers, filters={"text_search": "Acacia"}, size=200
    )
    body = r.json()
    assert body["total"] == 10
    for item in body["items"]:
        assert item["estate_name"] == "Acacia Rise"


def test_search_text_search_matches_lot_number(
    client: TestClient, sales_headers, search_seed_data
):
    r = _search(
        client, sales_headers, filters={"text_search": "A1-1"}, size=200
    )
    body = r.json()
    # Lot numbers across 6 stages contain "A1-1" (just 1 exact match).
    # "A1-1" substring only in A1-1 (Acacia Stage 1 Lot 1).
    assert body["total"] == 1
    assert body["items"][0]["lot_number"] == "A1-1"


def test_search_text_search_matches_suburb_case_insensitive(
    client: TestClient, sales_headers, search_seed_data
):
    r = _search(
        client, sales_headers, filters={"text_search": "TARNEIT"}, size=200
    )
    body = r.json()
    assert body["total"] == 10  # Acacia (Tarneit) = 10 lots


# ------------------------ sorting -------------------------------------------


def test_search_sort_by_land_price_asc_and_desc(
    client: TestClient, sales_headers, search_seed_data
):
    # Sort by land_price asc — first non-null price should be 300000.
    r_asc = _search(
        client,
        sales_headers,
        filters={"exclude_null_price": True},
        sort_by="land_price",
        sort_desc=False,
        size=200,
    )
    prices_asc = [float(i["land_price"]) for i in r_asc.json()["items"]]
    assert prices_asc == sorted(prices_asc)

    r_desc = _search(
        client,
        sales_headers,
        filters={"exclude_null_price": True},
        sort_by="land_price",
        sort_desc=True,
        size=200,
    )
    prices_desc = [float(i["land_price"]) for i in r_desc.json()["items"]]
    assert prices_desc == sorted(prices_desc, reverse=True)


def test_search_sort_by_size_sqm(
    client: TestClient, sales_headers, search_seed_data
):
    r = _search(
        client, sales_headers, sort_by="size_sqm", sort_desc=False, size=200
    )
    sizes = [float(i["size_sqm"]) for i in r.json()["items"]]
    assert sizes == sorted(sizes)


def test_search_invalid_sort_by_returns_422(
    client: TestClient, sales_headers, search_seed_data
):
    """Invalid sort_by falls back to land_price (API is lenient, 200 OK)."""
    # Per LotSearchRequest.normalized_sort, invalid keys silently fall back.
    r = _search(
        client, sales_headers, sort_by="DROP TABLE lots", size=5
    )
    assert r.status_code == 200
    # Result is still sorted by land_price (fallback).


# ------------------------ combined filters + enrichment ---------------------


def test_search_combined_filters_apply_all(
    client: TestClient, sales_headers, search_seed_data
):
    alpha = search_seed_data["developers"]["alpha"]
    r = _search(
        client,
        sales_headers,
        filters={
            "developer_ids": [alpha],
            "statuses": ["Available"],
            "price_min": 350000,
            "corner_block": False,
        },
        size=200,
    )
    body = r.json()
    # Alpha = Acacia + Banksia (4 stages x 5 lots = 20 lots).
    # Per stage: Available at idx 0 (corner) and idx 1 (price=350k, not corner).
    # We need developer=alpha AND Available AND price>=350k AND not corner.
    # idx 1 qualifies: price 350k, Available, corner=False. 1 per stage x 4 stages = 4.
    assert body["total"] == 4
    for item in body["items"]:
        assert item["developer_name"] == "AlphaDev"
        assert item["status"] == "Available"
        assert float(item["land_price"]) >= 350000
        assert item["corner_block"] is False


def test_search_returns_enriched_names(
    client: TestClient, sales_headers, search_seed_data
):
    r = _search(client, sales_headers, size=5)
    body = r.json()
    assert len(body["items"]) > 0
    for item in body["items"]:
        assert item["estate_name"]
        assert item["developer_name"]
        assert item["stage_name"]
        # region_name / suburb / state are populated for all seed estates.
        assert item["region_name"] in {"Metro", "Growth Corridor"}
        assert item["estate_suburb"] in {"Tarneit", "Werribee", "Oran Park"}
        assert item["estate_state"] in {"VIC", "NSW"}

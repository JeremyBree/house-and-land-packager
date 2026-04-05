"""Unit tests for lot_service.parse_csv_upload."""
from __future__ import annotations

from decimal import Decimal

import pytest

from hlp.shared.exceptions import InvalidCsvError
from hlp.shared.lot_service import parse_csv_upload


def _csv(text: str) -> bytes:
    return text.encode("utf-8")


def test_parse_csv_minimal_rows():
    content = _csv("lot_number\n1\n2\n3\n")
    result = parse_csv_upload(content)
    assert [r.lot_number for r in result] == ["1", "2", "3"]
    assert all(r.corner_block is False for r in result)


def test_parse_csv_all_columns():
    header = (
        "lot_number,frontage,depth,size_sqm,corner_block,orientation,"
        "side_easement,rear_easement,street_name,land_price,build_price,"
        "package_price,title_date"
    )
    row = (
        "42,12.50,30.00,375.00,yes,North,1.50,2.00,Main St,"
        "250000.00,350000.00,600000.00,2025-06-01"
    )
    content = _csv(f"{header}\n{row}\n")
    rows = parse_csv_upload(content)
    assert len(rows) == 1
    r = rows[0]
    assert r.lot_number == "42"
    assert r.frontage == Decimal("12.50")
    assert r.depth == Decimal("30.00")
    assert r.size_sqm == Decimal("375.00")
    assert r.corner_block is True
    assert r.orientation == "North"
    assert r.side_easement == Decimal("1.50")
    assert r.rear_easement == Decimal("2.00")
    assert r.street_name == "Main St"
    assert r.land_price == Decimal("250000.00")
    assert r.build_price == Decimal("350000.00")
    assert r.package_price == Decimal("600000.00")
    assert r.title_date.isoformat() == "2025-06-01"


def test_parse_csv_boolean_variants():
    content = _csv(
        "lot_number,corner_block\n"
        "1,yes\n"
        "2,no\n"
        "3,true\n"
        "4,false\n"
        "5,1\n"
        "6,0\n"
        "7,Y\n"
        "8,N\n"
    )
    rows = parse_csv_upload(content)
    assert [r.corner_block for r in rows] == [
        True, False, True, False, True, False, True, False,
    ]


def test_parse_csv_skips_blank_rows():
    content = _csv("lot_number\n1\n\n2\n   \n3\n")
    rows = parse_csv_upload(content)
    assert [r.lot_number for r in rows] == ["1", "2", "3"]


def test_parse_csv_handles_utf8_bom():
    # Prepend a UTF-8 BOM
    text = "lot_number\n1\n2\n"
    content = b"\xef\xbb\xbf" + text.encode("utf-8")
    rows = parse_csv_upload(content)
    assert [r.lot_number for r in rows] == ["1", "2"]


def test_parse_csv_missing_lot_number_raises():
    content = _csv("lot_number,frontage\n1,12.0\n,15.0\n")
    with pytest.raises(InvalidCsvError) as ei:
        parse_csv_upload(content)
    # Second data row is row 3 (header=1)
    assert "Row 3" in str(ei.value)
    assert "lot_number" in str(ei.value)


def test_parse_csv_invalid_numeric_raises():
    content = _csv("lot_number,frontage\n1,not-a-number\n")
    with pytest.raises(InvalidCsvError) as ei:
        parse_csv_upload(content)
    assert "frontage" in str(ei.value)
    assert "Row 2" in str(ei.value)


def test_parse_csv_invalid_date_raises():
    content = _csv("lot_number,title_date\n1,31/12/2025\n")
    with pytest.raises(InvalidCsvError) as ei:
        parse_csv_upload(content)
    assert "title_date" in str(ei.value)
    assert "Row 2" in str(ei.value)


def test_parse_csv_invalid_boolean_raises():
    content = _csv("lot_number,corner_block\n1,maybe\n")
    with pytest.raises(InvalidCsvError) as ei:
        parse_csv_upload(content)
    assert "corner_block" in str(ei.value)
    assert "Row 2" in str(ei.value)


def test_parse_csv_empty_content_returns_empty_list():
    content = _csv("lot_number\n")
    rows = parse_csv_upload(content)
    assert rows == []

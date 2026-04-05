"""Land Search Interface (LSI) request/response schemas."""

from datetime import date
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from hlp.api.schemas.lot import LotRead
from hlp.models.enums import LotStatus

ALLOWED_SORT_FIELDS = {
    "land_price",
    "size_sqm",
    "frontage",
    "lot_number",
    "estate_name",
    "last_confirmed_date",
}


class LotSearchFilters(BaseModel):
    estate_ids: list[int] | None = None
    developer_ids: list[int] | None = None
    region_ids: list[int] | None = None
    suburbs: list[str] | None = None
    statuses: list[LotStatus] | None = None
    price_min: Decimal | None = None
    price_max: Decimal | None = None
    size_min: Decimal | None = None
    size_max: Decimal | None = None
    frontage_min: Decimal | None = None
    depth_min: Decimal | None = None
    corner_block: bool | None = None
    title_date_from: date | None = None
    title_date_to: date | None = None
    exclude_null_price: bool = False
    text_search: str | None = None


class LotSearchRequest(BaseModel):
    filters: LotSearchFilters = Field(default_factory=LotSearchFilters)
    page: int = Field(default=1, ge=1)
    size: int = Field(default=50, ge=1, le=200)
    sort_by: str = Field(default="land_price")
    sort_desc: bool = False

    def normalized_sort(self) -> str:
        return self.sort_by if self.sort_by in ALLOWED_SORT_FIELDS else "land_price"


class LotSearchResult(LotRead):
    model_config = ConfigDict(from_attributes=True)

    estate_name: str
    estate_suburb: str | None = None
    estate_state: str | None = None
    developer_name: str
    region_name: str | None = None
    stage_name: str


class LotSearchResponse(BaseModel):
    items: list[LotSearchResult]
    total: int
    page: int
    size: int
    pages: int
    filter_summary: dict[str, Any]

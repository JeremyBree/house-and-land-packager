"""PricingRequest request/response schemas."""

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class LotEntry(BaseModel):
    lot_number: str = Field(min_length=1, max_length=50)
    house_type: str = Field(min_length=1, max_length=255)
    facade_type: str = Field(min_length=1, max_length=255)
    garage_side: str | None = Field(default=None, max_length=50)
    custom_house_design: bool | None = None


class PricingRequestCreate(BaseModel):
    estate_id: int
    stage_id: int
    brand: str = Field(min_length=1, max_length=100)
    has_land_titled: bool
    titling_when: date | None = None
    is_kdrb: bool = False
    is_10_90_deal: bool = False
    developer_land_referrals: bool = False
    building_crossover: bool = False
    shared_crossovers: bool = False
    side_easement: Decimal | None = None
    rear_easement: Decimal | None = None
    bdm: str | None = Field(default=None, max_length=255)
    wholesale_group: str | None = Field(default=None, max_length=255)
    lots: list[LotEntry] = Field(min_length=1)
    notes: str | None = None

    @model_validator(mode="after")
    def _validate_brand_fields(self):
        if self.brand == "Hermitage Homes":
            if not self.bdm:
                raise ValueError("bdm is required for Hermitage Homes")
            if not self.wholesale_group:
                raise ValueError("wholesale_group is required for Hermitage Homes")
        return self


class PricingRequestRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    request_id: int
    requester_id: int
    estate_id: int
    stage_id: int
    brand: str
    status: str
    form_data: dict
    generated_file_path: str | None = None
    completed_file_path: str | None = None
    lot_numbers: list[str]
    submitted_at: datetime | None = None
    completed_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class PricingRequestDetailRead(PricingRequestRead):
    requester_name: str | None = None
    estate_name: str | None = None
    stage_name: str | None = None


class PricingRequestListQuery(BaseModel):
    page: int = Field(default=1, ge=1)
    size: int = Field(default=25, ge=1, le=200)
    status: str | None = None
    brand: str | None = None
    estate_id: int | None = None


class ClashViolation(BaseModel):
    lot_numbers: list[str]
    design: str
    facade: str
    rule_id: int | None = None
    violation_type: str = "within_request"

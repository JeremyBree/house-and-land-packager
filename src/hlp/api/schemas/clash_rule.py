"""ClashRule request/response schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ClashRuleCreate(BaseModel):
    estate_id: int
    stage_id: int
    lot_number: str = Field(min_length=1, max_length=50)
    cannot_match: list[str] = Field(default_factory=list)


class ClashRuleUpdate(BaseModel):
    cannot_match: list[str] = Field(default_factory=list)


class ClashRuleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    rule_id: int
    estate_id: int
    stage_id: int
    lot_number: str
    cannot_match: list[str]
    created_at: datetime


class ClashRuleCopyRequest(BaseModel):
    target_estate_id: int
    target_stage_id: int

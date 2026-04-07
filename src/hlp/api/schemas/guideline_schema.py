"""Guideline type & estate design guideline request/response schemas."""

from pydantic import BaseModel, ConfigDict, Field


# ---- GuidelineType -----------------------------------------------------------

class GuidelineTypeCreate(BaseModel):
    short_name: str = Field(min_length=1, max_length=100)
    description: str = Field(min_length=1)
    sort_order: int = 0


class GuidelineTypeUpdate(BaseModel):
    short_name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, min_length=1)
    sort_order: int | None = None


class GuidelineTypeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    type_id: int
    short_name: str
    description: str
    sort_order: int


# ---- EstateDesignGuideline ---------------------------------------------------

class EstateGuidelineCreate(BaseModel):
    estate_id: int
    stage_id: int | None = None
    type_id: int
    cost: float | None = None
    override_text: str | None = None


class EstateGuidelineUpdate(BaseModel):
    estate_id: int | None = None
    stage_id: int | None = None
    type_id: int | None = None
    cost: float | None = None
    override_text: str | None = None


class EstateGuidelineRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    guideline_id: int
    estate_id: int
    stage_id: int | None = None
    type_id: int
    guideline_type_name: str | None = None
    cost: float | None = None
    override_text: str | None = None

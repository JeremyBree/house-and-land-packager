"""Guideline type & estate design guideline request/response schemas."""

from pydantic import BaseModel, ConfigDict, Field


# ---- GuidelineType -----------------------------------------------------------

class GuidelineTypeCreate(BaseModel):
    short_name: str = Field(min_length=1, max_length=100)
    description: str = Field(min_length=1)
    sort_order: int = 0
    category_code: str | None = None
    category_name: str | None = None
    notes: str | None = None
    default_price: float = 0


class GuidelineTypeUpdate(BaseModel):
    short_name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, min_length=1)
    sort_order: int | None = None
    category_code: str | None = None
    category_name: str | None = None
    notes: str | None = None
    default_price: float | None = None


class GuidelineTypeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    type_id: int
    short_name: str
    description: str
    sort_order: int
    category_code: str | None = None
    category_name: str | None = None
    notes: str | None = None
    default_price: float = 0


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
    default_price: float | None = None
    category_description: str | None = None


class GuidelineCopyRequest(BaseModel):
    source_estate_id: int
    source_stage_id: int | None = None
    target_estate_id: int
    target_stage_id: int | None = None

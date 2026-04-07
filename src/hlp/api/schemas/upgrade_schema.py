"""Upgrade category & item request/response schemas."""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


# ---- Category ----------------------------------------------------------------

class UpgradeCategoryCreate(BaseModel):
    brand: str = Field(min_length=1, max_length=100)
    name: str = Field(min_length=1, max_length=100)
    sort_order: int = 0


class UpgradeCategoryUpdate(BaseModel):
    brand: str | None = Field(default=None, min_length=1, max_length=100)
    name: str | None = Field(default=None, min_length=1, max_length=100)
    sort_order: int | None = None


class UpgradeCategoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    category_id: int
    brand: str
    name: str
    sort_order: int


# ---- Item --------------------------------------------------------------------

class UpgradeItemCreate(BaseModel):
    brand: str = Field(min_length=1, max_length=100)
    category_id: int | None = None
    description: str = Field(min_length=1)
    price: float
    date_added: date | None = None
    notes: str | None = None
    sort_order: int = 0


class UpgradeItemUpdate(BaseModel):
    brand: str | None = Field(default=None, min_length=1, max_length=100)
    category_id: int | None = None
    description: str | None = Field(default=None, min_length=1)
    price: float | None = None
    date_added: date | None = None
    notes: str | None = None
    sort_order: int | None = None


class UpgradeItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    upgrade_id: int
    brand: str
    category_id: int | None = None
    category_name: str | None = None
    description: str
    price: float
    date_added: date | None = None
    notes: str | None = None
    sort_order: int
    created_at: datetime
    updated_at: datetime

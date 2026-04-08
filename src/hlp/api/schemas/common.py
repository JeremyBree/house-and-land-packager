"""Common API schemas."""

from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    size: int
    pages: int


class CsvRowError(BaseModel):
    row: int
    error: str


class CsvUploadResult(BaseModel):
    created: int
    skipped: int
    errors: list[CsvRowError] = Field(default_factory=list)


class ErrorResponse(BaseModel):
    detail: str
    code: str | None = None

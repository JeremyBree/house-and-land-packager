"""Conflict response schemas."""

from pydantic import BaseModel

from hlp.api.schemas.house_package import PackageRead


class ConflictEstateCount(BaseModel):
    estate_id: int
    estate_name: str
    count: int


class ConflictRead(BaseModel):
    conflict_type: str  # 'design-facade' | 'design-facade-colour'
    severity: str  # 'high' | 'critical'
    package_a: PackageRead
    package_b: PackageRead
    rule_id: int
    estate_id: int
    stage_id: int
    lot_numbers: list[str]


class ConflictSummary(BaseModel):
    total_conflicts: int
    by_type: dict[str, int]
    by_estate: list[ConflictEstateCount]

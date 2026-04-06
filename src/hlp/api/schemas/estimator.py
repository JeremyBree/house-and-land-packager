"""Estimator workflow schemas."""

from decimal import Decimal

from pydantic import BaseModel


class LotSiteCostInput(BaseModel):
    """Estimator's per-lot site cost inputs."""

    lot_number: str
    fall_mm: int = 0
    fill_trees: bool = False
    easement_proximity_lhs: bool = False
    easement_proximity_rhs: bool = False
    retaining_lhs: bool = False
    retaining_rhs: bool = False
    rock_removal: bool = False
    rear_setback_m: Decimal = Decimal("0")
    existing_neighbours: bool = False
    notes: str | None = None


class EstimatorSubmission(BaseModel):
    """Estimator submits site costs for all lots in a request."""

    lot_inputs: list[LotSiteCostInput]


class EstimatorAssignment(BaseModel):
    """Assign an estimator to a request."""

    estimator_id: int

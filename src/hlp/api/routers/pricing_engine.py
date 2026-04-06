"""Pricing engine calculation router."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from hlp.api.deps import get_current_user, get_db
from hlp.api.schemas.pricing_engine_schema import (
    PriceBreakdownResponse,
    PricingCalculateRequest,
)
from hlp.shared.pricing_engine import (
    LotPricingInput,
    PricingContext,
    calculate_batch,
)

router = APIRouter(prefix="/api/pricing", tags=["pricing-engine"])


@router.post(
    "/calculate",
    response_model=list[PriceBreakdownResponse],
    dependencies=[Depends(get_current_user)],
)
def calculate_pricing(
    payload: PricingCalculateRequest,
    db: Annotated[Session, Depends(get_db)],
) -> list[PriceBreakdownResponse]:
    """Preview price breakdown -- does NOT create a pricing request."""
    ctx = PricingContext(
        estate_id=payload.context.estate_id,
        stage_id=payload.context.stage_id,
        brand=payload.context.brand,
        suburb=payload.context.suburb,
        postcode=payload.context.postcode,
        bdm_profile_id=payload.context.bdm_profile_id,
        wholesale_group_name=payload.context.wholesale_group_name,
        is_kdrb=payload.context.is_kdrb,
        is_10_90_deal=payload.context.is_10_90_deal,
        holding_costs_apply=payload.context.holding_costs_apply,
        developer_land_referrals=payload.context.developer_land_referrals,
        building_crossover=payload.context.building_crossover,
        shared_crossovers=payload.context.shared_crossovers,
        pricing_date=payload.context.pricing_date,
        contract_date=payload.context.contract_date,
    )

    lots = [
        LotPricingInput(
            lot_number=lot.lot_number,
            lot_frontage=lot.lot_frontage,
            lot_depth=lot.lot_depth,
            lot_size_sqm=lot.lot_size_sqm,
            land_price=lot.land_price,
            corner_block=lot.corner_block,
            orientation=lot.orientation,
            house_name=lot.house_name,
            facade_name=lot.facade_name,
            garage_side=lot.garage_side,
            fall_mm=lot.fall_mm,
            fill_trees=lot.fill_trees,
            easement_proximity_lhs=lot.easement_proximity_lhs,
            easement_proximity_rhs=lot.easement_proximity_rhs,
            retaining_lhs=lot.retaining_lhs,
            retaining_rhs=lot.retaining_rhs,
        )
        for lot in payload.lots
    ]

    breakdowns = calculate_batch(db, ctx, lots)
    return [PriceBreakdownResponse(**bd.to_dict()) for bd in breakdowns]

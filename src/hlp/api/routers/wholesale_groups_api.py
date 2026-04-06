"""Wholesale groups router."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from hlp.api.deps import get_current_user, get_db
from hlp.api.schemas.wholesale_group_schema import WholesaleGroupRead
from hlp.repositories import commission_repository

router = APIRouter(prefix="/api/wholesale-groups", tags=["wholesale-groups"])


@router.get("", response_model=list[WholesaleGroupRead], dependencies=[Depends(get_current_user)])
def list_wholesale_groups(
    db: Annotated[Session, Depends(get_db)],
    bdm_id: int | None = Query(default=None),
) -> list[WholesaleGroupRead]:
    if bdm_id is not None:
        # Filter groups that have commission rates for this BDM
        from sqlalchemy import select
        from hlp.models.commission_rate import CommissionRate
        from hlp.models.wholesale_group import WholesaleGroup

        stmt = (
            select(WholesaleGroup)
            .join(CommissionRate, CommissionRate.group_id == WholesaleGroup.group_id)
            .where(CommissionRate.bdm_profile_id == bdm_id)
            .order_by(WholesaleGroup.group_name)
        )
        groups = list(db.execute(stmt).scalars().all())
    else:
        groups = commission_repository.list_wholesale_groups(db)
    return [WholesaleGroupRead.model_validate(g) for g in groups]

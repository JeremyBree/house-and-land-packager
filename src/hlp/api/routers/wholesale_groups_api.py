"""Wholesale groups and commission rates router."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from hlp.api.deps import get_current_user, get_db, require_admin
from hlp.api.schemas.wholesale_group_schema import (
    WholesaleGroupCreate,
    WholesaleGroupRead,
    WholesaleGroupUpdate,
)
from hlp.api.schemas.commission_rate_schema import (
    CommissionRateCreate,
    CommissionRateRead,
    CommissionRateUpdate,
)
from hlp.repositories import commission_repository

router = APIRouter(tags=["wholesale-groups"])

# ---------------------------------------------------------------------------
# Wholesale Groups  /api/wholesale-groups
# ---------------------------------------------------------------------------

wg_prefix = "/api/wholesale-groups"


@router.get(wg_prefix, response_model=list[WholesaleGroupRead], dependencies=[Depends(get_current_user)])
def list_wholesale_groups(
    db: Annotated[Session, Depends(get_db)],
    bdm_id: int | None = Query(default=None),
    include_inactive: bool = Query(default=False),
) -> list[WholesaleGroupRead]:
    if bdm_id is not None:
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
        active_only = not include_inactive
        groups = commission_repository.list_wholesale_groups(db, active=active_only)
    return [WholesaleGroupRead.model_validate(g) for g in groups]


@router.post(wg_prefix, response_model=WholesaleGroupRead, dependencies=[Depends(require_admin)])
def create_wholesale_group(
    body: WholesaleGroupCreate,
    db: Annotated[Session, Depends(get_db)],
) -> WholesaleGroupRead:
    wg = commission_repository.create_wholesale_group(
        db,
        group_name=body.group_name,
        gst_registered=body.gst_registered,
        active=body.active,
    )
    db.commit()
    db.refresh(wg)
    return WholesaleGroupRead.model_validate(wg)


@router.patch(wg_prefix + "/{group_id}", response_model=WholesaleGroupRead, dependencies=[Depends(require_admin)])
def update_wholesale_group(
    group_id: int,
    body: WholesaleGroupUpdate,
    db: Annotated[Session, Depends(get_db)],
) -> WholesaleGroupRead:
    fields = body.model_dump(exclude_unset=True)
    wg = commission_repository.update_wholesale_group(db, group_id, **fields)
    if wg is None:
        raise HTTPException(status_code=404, detail="Wholesale group not found")
    db.commit()
    db.refresh(wg)
    return WholesaleGroupRead.model_validate(wg)


@router.delete(wg_prefix + "/{group_id}", status_code=204, dependencies=[Depends(require_admin)])
def delete_wholesale_group(
    group_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> None:
    ok = commission_repository.delete_wholesale_group(db, group_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Wholesale group not found")
    db.commit()


# ---------------------------------------------------------------------------
# Commission Rates  /api/commission-rates
# ---------------------------------------------------------------------------

cr_prefix = "/api/commission-rates"


def _to_rate_read(cr) -> CommissionRateRead:
    bdm_name = None
    if cr.bdm:
        bdm_name = f"{cr.bdm.first_name} {cr.bdm.last_name}"
    group_name = cr.wholesale_group.group_name if cr.wholesale_group else None
    return CommissionRateRead(
        rate_id=cr.rate_id,
        bdm_profile_id=cr.bdm_profile_id,
        group_id=cr.group_id,
        commission_fixed=float(cr.commission_fixed) if cr.commission_fixed is not None else None,
        commission_pct=float(cr.commission_pct) if cr.commission_pct is not None else None,
        brand=cr.brand,
        bdm_name=bdm_name,
        group_name=group_name,
    )


@router.get(cr_prefix, response_model=list[CommissionRateRead], dependencies=[Depends(get_current_user)])
def list_commission_rates(
    db: Annotated[Session, Depends(get_db)],
    brand: str | None = Query(default=None),
    group_id: int | None = Query(default=None),
) -> list[CommissionRateRead]:
    rates = commission_repository.list_commission_rates(db, brand=brand, group_id=group_id)
    return [_to_rate_read(r) for r in rates]


@router.post(cr_prefix, response_model=CommissionRateRead, dependencies=[Depends(require_admin)])
def create_commission_rate(
    body: CommissionRateCreate,
    db: Annotated[Session, Depends(get_db)],
) -> CommissionRateRead:
    cr = commission_repository.create_commission_rate(
        db,
        bdm_profile_id=body.bdm_profile_id,
        group_id=body.group_id,
        brand=body.brand,
        commission_fixed=body.commission_fixed,
        commission_pct=body.commission_pct,
    )
    db.commit()
    cr = commission_repository.get_commission_rate(db, cr.rate_id)
    return _to_rate_read(cr)


@router.patch(cr_prefix + "/{rate_id}", response_model=CommissionRateRead, dependencies=[Depends(require_admin)])
def update_commission_rate(
    rate_id: int,
    body: CommissionRateUpdate,
    db: Annotated[Session, Depends(get_db)],
) -> CommissionRateRead:
    fields = body.model_dump(exclude_unset=True)
    cr = commission_repository.update_commission_rate(db, rate_id, **fields)
    if cr is None:
        raise HTTPException(status_code=404, detail="Commission rate not found")
    db.commit()
    cr = commission_repository.get_commission_rate(db, rate_id)
    return _to_rate_read(cr)


@router.delete(cr_prefix + "/{rate_id}", status_code=204, dependencies=[Depends(require_admin)])
def delete_commission_rate(
    rate_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> None:
    ok = commission_repository.delete_commission_rate(db, rate_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Commission rate not found")
    db.commit()

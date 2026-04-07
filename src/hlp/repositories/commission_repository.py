"""Commission rate + wholesale group data access."""

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from hlp.models.commission_rate import CommissionRate
from hlp.models.wholesale_group import WholesaleGroup


# ---------------------------------------------------------------------------
# Wholesale Groups
# ---------------------------------------------------------------------------


def get_rate(
    db: Session, bdm_profile_id: int | None, wholesale_group_name: str | None
) -> CommissionRate | None:
    if bdm_profile_id is None or wholesale_group_name is None:
        return None
    # Resolve group_id from name
    group = db.execute(
        select(WholesaleGroup).where(WholesaleGroup.group_name == wholesale_group_name)
    ).scalars().first()
    if group is None:
        return None
    stmt = (
        select(CommissionRate)
        .where(
            CommissionRate.bdm_profile_id == bdm_profile_id,
            CommissionRate.group_id == group.group_id,
        )
        .options(joinedload(CommissionRate.wholesale_group))
    )
    return db.execute(stmt).unique().scalars().first()


def list_wholesale_groups(db: Session, active: bool = True) -> list[WholesaleGroup]:
    stmt = select(WholesaleGroup).order_by(WholesaleGroup.group_name)
    if active:
        stmt = stmt.where(WholesaleGroup.active.is_(True))
    return list(db.execute(stmt).scalars().all())


def get_wholesale_group(db: Session, group_id: int) -> WholesaleGroup | None:
    return db.get(WholesaleGroup, group_id)


def create_wholesale_group(
    db: Session,
    *,
    group_name: str,
    gst_registered: bool = False,
    active: bool = True,
) -> WholesaleGroup:
    wg = WholesaleGroup(
        group_name=group_name,
        gst_registered=gst_registered,
        active=active,
    )
    db.add(wg)
    db.flush()
    return wg


def update_wholesale_group(
    db: Session,
    group_id: int,
    **fields: object,
) -> WholesaleGroup | None:
    wg = db.get(WholesaleGroup, group_id)
    if wg is None:
        return None
    for k, v in fields.items():
        if hasattr(wg, k):
            setattr(wg, k, v)
    db.flush()
    return wg


def delete_wholesale_group(db: Session, group_id: int) -> bool:
    wg = db.get(WholesaleGroup, group_id)
    if wg is None:
        return False
    db.delete(wg)
    db.flush()
    return True


# ---------------------------------------------------------------------------
# Commission Rates
# ---------------------------------------------------------------------------


def list_commission_rates(
    db: Session,
    *,
    brand: str | None = None,
    group_id: int | None = None,
) -> list[CommissionRate]:
    stmt = (
        select(CommissionRate)
        .options(
            joinedload(CommissionRate.wholesale_group),
            joinedload(CommissionRate.bdm),
        )
        .order_by(CommissionRate.rate_id)
    )
    if brand is not None:
        stmt = stmt.where(CommissionRate.brand == brand)
    if group_id is not None:
        stmt = stmt.where(CommissionRate.group_id == group_id)
    return list(db.execute(stmt).unique().scalars().all())


def get_commission_rate(db: Session, rate_id: int) -> CommissionRate | None:
    stmt = (
        select(CommissionRate)
        .where(CommissionRate.rate_id == rate_id)
        .options(
            joinedload(CommissionRate.wholesale_group),
            joinedload(CommissionRate.bdm),
        )
    )
    return db.execute(stmt).unique().scalars().first()


def create_commission_rate(
    db: Session,
    *,
    bdm_profile_id: int,
    group_id: int,
    brand: str,
    commission_fixed: float | None = None,
    commission_pct: float | None = None,
) -> CommissionRate:
    cr = CommissionRate(
        bdm_profile_id=bdm_profile_id,
        group_id=group_id,
        brand=brand,
        commission_fixed=commission_fixed,
        commission_pct=commission_pct,
    )
    db.add(cr)
    db.flush()
    # Re-fetch with relationships loaded
    return get_commission_rate(db, cr.rate_id)  # type: ignore[return-value]


def update_commission_rate(
    db: Session,
    rate_id: int,
    **fields: object,
) -> CommissionRate | None:
    cr = db.get(CommissionRate, rate_id)
    if cr is None:
        return None
    for k, v in fields.items():
        if hasattr(cr, k):
            setattr(cr, k, v)
    db.flush()
    return get_commission_rate(db, rate_id)


def delete_commission_rate(db: Session, rate_id: int) -> bool:
    cr = db.get(CommissionRate, rate_id)
    if cr is None:
        return False
    db.delete(cr)
    db.flush()
    return True

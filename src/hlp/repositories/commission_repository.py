"""Commission rate + wholesale group data access."""

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from hlp.models.commission_rate import CommissionRate
from hlp.models.wholesale_group import WholesaleGroup


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

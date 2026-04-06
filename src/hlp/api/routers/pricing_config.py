"""Pricing config router — admin-configurable pricing engine constants."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from hlp.api.deps import get_current_user, get_db, require_admin
from hlp.api.schemas.pricing_config import PricingConfigRead, PricingConfigUpdate
from hlp.models.pricing_config import PricingConfig
from hlp.models.profile import Profile

router = APIRouter(prefix="/api/pricing-config", tags=["pricing-config"])


@router.get(
    "/{brand}",
    response_model=PricingConfigRead,
    dependencies=[Depends(get_current_user)],
)
def get_pricing_config(
    brand: str,
    db: Annotated[Session, Depends(get_db)],
) -> PricingConfigRead:
    """Get pricing config for a brand. Returns defaults if none exists."""
    config = db.execute(
        select(PricingConfig).where(PricingConfig.brand == brand)
    ).scalars().first()
    if config is None:
        # Return a default config (not persisted)
        config = PricingConfig(config_id=0, brand=brand)
    return PricingConfigRead.model_validate(config)


@router.patch(
    "/{brand}",
    response_model=PricingConfigRead,
)
def update_pricing_config(
    brand: str,
    payload: PricingConfigUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Profile, Depends(require_admin)],
) -> PricingConfigRead:
    """Update pricing config for a brand. Creates if not exists."""
    config = db.execute(
        select(PricingConfig).where(PricingConfig.brand == brand)
    ).scalars().first()

    if config is None:
        config = PricingConfig(brand=brand)
        db.add(config)
        db.flush()

    updates = payload.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(config, key, value)
    db.flush()
    db.commit()
    db.refresh(config)
    return PricingConfigRead.model_validate(config)

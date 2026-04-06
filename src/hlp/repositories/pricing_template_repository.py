"""PricingTemplate data access."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from hlp.models.pricing_template import PricingTemplate


def get_by_id(db: Session, template_id: int) -> PricingTemplate | None:
    return db.get(PricingTemplate, template_id)


def get_by_brand(db: Session, brand: str) -> PricingTemplate | None:
    stmt = select(PricingTemplate).where(PricingTemplate.brand == brand)
    return db.execute(stmt).scalar_one_or_none()


def list_all(db: Session) -> list[PricingTemplate]:
    stmt = select(PricingTemplate).order_by(PricingTemplate.brand)
    return list(db.execute(stmt).scalars().all())


def create(db: Session, **fields) -> PricingTemplate:
    template = PricingTemplate(**fields)
    db.add(template)
    db.flush()
    return template


def update(db: Session, template: PricingTemplate, **fields) -> PricingTemplate:
    for key, value in fields.items():
        if value is not None:
            setattr(template, key, value)
    db.flush()
    return template


def upsert_by_brand(db: Session, brand: str, **fields) -> PricingTemplate:
    """Create or update the template for a brand."""
    existing = get_by_brand(db, brand)
    if existing is None:
        return create(db, brand=brand, **fields)
    return update(db, existing, **fields)

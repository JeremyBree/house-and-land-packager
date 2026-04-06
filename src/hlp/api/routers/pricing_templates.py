"""Pricing template router."""

from typing import Annotated

from fastapi import APIRouter, Depends, UploadFile, status
from sqlalchemy.orm import Session

from hlp.api.deps import get_current_user, get_db, require_admin
from hlp.api.schemas.pricing_template import (
    DataValidationsRead,
    TemplateRead,
    TemplateUpdateMappings,
)
from hlp.repositories import pricing_template_repository
from hlp.shared import template_service
from hlp.shared.exceptions import TemplateNotFoundError

router = APIRouter(prefix="/api/pricing-templates", tags=["pricing-templates"])

# Brand slug → full brand name
_BRAND_SLUGS = {
    "hermitage": "Hermitage Homes",
    "kingsbridge": "Kingsbridge Homes",
}


def _resolve_brand(brand_slug: str) -> str:
    brand = _BRAND_SLUGS.get(brand_slug.lower())
    if brand is None:
        raise TemplateNotFoundError(
            f"Unknown brand slug '{brand_slug}'. Use 'hermitage' or 'kingsbridge'."
        )
    return brand


@router.get(
    "",
    response_model=list[TemplateRead],
    dependencies=[Depends(require_admin)],
)
def list_templates(
    db: Annotated[Session, Depends(get_db)],
) -> list[TemplateRead]:
    templates = pricing_template_repository.list_all(db)
    return [TemplateRead.model_validate(t) for t in templates]


@router.get(
    "/{brand_slug}",
    response_model=TemplateRead,
    dependencies=[Depends(get_current_user)],
)
def get_template_by_brand(
    brand_slug: str,
    db: Annotated[Session, Depends(get_db)],
) -> TemplateRead:
    brand = _resolve_brand(brand_slug)
    template = template_service.get_template_for_brand(db, brand)
    if template is None:
        raise TemplateNotFoundError(f"No template uploaded for {brand}")
    return TemplateRead.model_validate(template)


@router.post(
    "/{brand_slug}/upload",
    response_model=TemplateRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)],
)
async def upload_template(
    brand_slug: str,
    file: UploadFile,
    db: Annotated[Session, Depends(get_db)],
) -> TemplateRead:
    brand = _resolve_brand(brand_slug)
    content = await file.read()
    filename = file.filename or "template.xlsx"
    template = template_service.upload_template(db, brand, content, filename)
    db.commit()
    db.refresh(template)
    return TemplateRead.model_validate(template)


@router.patch(
    "/{template_id}/mappings",
    response_model=TemplateRead,
    dependencies=[Depends(require_admin)],
)
def update_template_mappings(
    template_id: int,
    payload: TemplateUpdateMappings,
    db: Annotated[Session, Depends(get_db)],
) -> TemplateRead:
    template = template_service.update_template_mappings(
        db,
        template_id,
        sheet_name=payload.sheet_name,
        data_start_row=payload.data_start_row,
        header_mappings=payload.header_mappings,
        column_mappings=payload.column_mappings,
    )
    db.commit()
    db.refresh(template)
    return TemplateRead.model_validate(template)


@router.get(
    "/{brand_slug}/validations",
    response_model=DataValidationsRead,
    dependencies=[Depends(get_current_user)],
)
def get_data_validations(
    brand_slug: str,
    db: Annotated[Session, Depends(get_db)],
) -> DataValidationsRead:
    brand = _resolve_brand(brand_slug)
    template = template_service.get_template_for_brand(db, brand)
    if template is None:
        raise TemplateNotFoundError(f"No template uploaded for {brand}")
    return DataValidationsRead(validations=template.data_validations or {})

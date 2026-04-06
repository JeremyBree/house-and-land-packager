"""Pricing calculation engine -- replaces Excel formula logic.

Computes a full price breakdown for each lot in a pricing request by
reading from the pricing engine tables (house_designs, facades, energy_ratings,
site_costs, guidelines, upgrades, commissions, etc.).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import ROUND_UP, Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from hlp.models.commission_rate import CommissionRate
from hlp.models.energy_rating import EnergyRating
from hlp.models.fbc_escalation import FbcEscalationBand
from hlp.models.house_design import HouseDesign, HouseFacade
from hlp.models.postcode_site_cost import PostcodeSiteCost
from hlp.models.site_cost import SiteCostItem, SiteCostTier
from hlp.models.guideline import EstateDesignGuideline
from hlp.models.upgrade import UpgradeItem
from hlp.models.wholesale_group import WholesaleGroup

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
LANDSCAPING_RATE_PER_SQM = Decimal("39")
BASE_COMMISSION = Decimal("33000")
PCT_COMMISSION_DIVISOR = Decimal("0.934")  # 1 - 0.066
KDRB_SURCHARGE = Decimal("25000")
HOLDING_COST_RATE = Decimal("0.10")
SMALL_LOT_THRESHOLD = Decimal("300")
SMALL_LOT_DISCOUNT = Decimal("5000")
DWELLINGS_DISCOUNT = Decimal("3000")
CORNER_BLOCK_SAVINGS = Decimal("4620")  # Saved when no corner blocks in batch

NEUTRALIZING_FACADES = frozenset({
    "Holt", "Traditional", "Prominent", "Elite", "Sorrento",
})

LATROBE_VALLEY_POSTCODES = frozenset({
    "3825", "3840", "3844", "3842", "3870", "3854", "3856", "3869",
})


# ---------------------------------------------------------------------------
# Input / Output dataclasses
# ---------------------------------------------------------------------------
@dataclass
class LotPricingInput:
    """Input for pricing a single lot."""

    lot_number: str
    lot_frontage: Decimal
    lot_depth: Decimal
    lot_size_sqm: Decimal
    land_price: Decimal
    corner_block: bool
    orientation: str  # N, NE, E, SE, S, SW, W, NW
    house_name: str
    facade_name: str
    garage_side: str  # 'Left' or 'Right'
    # Site-specific inputs
    fall_mm: int = 0
    fill_trees: bool = False
    easement_proximity_lhs: bool = False
    easement_proximity_rhs: bool = False
    retaining_lhs: bool = False
    retaining_rhs: bool = False


@dataclass
class PricingContext:
    """Shared context for the entire pricing request."""

    estate_id: int
    stage_id: int
    brand: str
    suburb: str
    postcode: str
    bdm_profile_id: int | None = None
    wholesale_group_name: str | None = None
    is_kdrb: bool = False
    is_10_90_deal: bool = False
    holding_costs_apply: bool = False
    developer_land_referrals: bool = False
    building_crossover: bool = False
    shared_crossovers: bool = False
    pricing_date: date = field(default_factory=date.today)
    contract_date: date | None = None


@dataclass
class PriceLineItem:
    """A single line in the price breakdown."""

    name: str
    amount: Decimal
    category: str  # house, facade, energy, site_cost, guideline, landscaping, upgrade, discount, commission, fbc, kdrb, holding
    detail: str | None = None


@dataclass
class PriceBreakdown:
    """Full price breakdown for a single lot."""

    lot_number: str
    house_name: str
    facade_name: str

    house_price: Decimal = Decimal("0")
    facade_price: Decimal = Decimal("0")
    energy_compliance_cost: Decimal = Decimal("0")
    site_costs_total: Decimal = Decimal("0")
    design_guidelines_total: Decimal = Decimal("0")
    extra_landscaping: Decimal = Decimal("0")
    extra_landscaping_sqm: Decimal = Decimal("0")
    upgrades_total: Decimal = Decimal("0")
    discount: Decimal = Decimal("0")
    discount_reason: str | None = None
    kdrb_surcharge: Decimal = Decimal("0")
    fbc_escalation_pct: Decimal = Decimal("0")
    fbc_escalation_amount: Decimal = Decimal("0")
    holding_costs: Decimal = Decimal("0")

    commission_fixed: Decimal | None = None
    commission_pct: Decimal | None = None
    comms_adjustment: Decimal = Decimal("0")

    total_build_price: Decimal = Decimal("0")
    total_package_price: Decimal = Decimal("0")
    land_price: Decimal = Decimal("0")

    house_fits: bool = True
    house_fits_reason: str | None = None
    extra_fence_meterage: Decimal = Decimal("0")

    line_items: list[PriceLineItem] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to JSON-serializable dict for storing in price_breakdown JSONB."""
        return {
            "lot_number": self.lot_number,
            "house_name": self.house_name,
            "facade_name": self.facade_name,
            "house_price": str(self.house_price),
            "facade_price": str(self.facade_price),
            "energy_compliance_cost": str(self.energy_compliance_cost),
            "site_costs_total": str(self.site_costs_total),
            "design_guidelines_total": str(self.design_guidelines_total),
            "extra_landscaping": str(self.extra_landscaping),
            "extra_landscaping_sqm": str(self.extra_landscaping_sqm),
            "upgrades_total": str(self.upgrades_total),
            "discount": str(self.discount),
            "discount_reason": self.discount_reason,
            "kdrb_surcharge": str(self.kdrb_surcharge),
            "fbc_escalation_pct": str(self.fbc_escalation_pct),
            "fbc_escalation_amount": str(self.fbc_escalation_amount),
            "holding_costs": str(self.holding_costs),
            "commission_fixed": str(self.commission_fixed) if self.commission_fixed is not None else None,
            "commission_pct": str(self.commission_pct) if self.commission_pct is not None else None,
            "comms_adjustment": str(self.comms_adjustment),
            "total_build_price": str(self.total_build_price),
            "total_package_price": str(self.total_package_price),
            "land_price": str(self.land_price),
            "house_fits": self.house_fits,
            "house_fits_reason": self.house_fits_reason,
            "extra_fence_meterage": str(self.extra_fence_meterage),
            "line_items": [
                {"name": li.name, "amount": str(li.amount), "category": li.category, "detail": li.detail}
                for li in self.line_items
            ],
            "warnings": self.warnings,
        }


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _dec(value: float | int | None) -> Decimal:
    """Safely convert a float/int/None to Decimal."""
    if value is None:
        return Decimal("0")
    return Decimal(str(value))


def _round_up_100(value: Decimal) -> Decimal:
    """Round up to the nearest $100."""
    return (value / Decimal("100")).quantize(Decimal("1"), rounding=ROUND_UP) * Decimal("100")


# ---------------------------------------------------------------------------
# Step functions
# ---------------------------------------------------------------------------
def _lookup_house(db: Session, brand: str, house_name: str) -> HouseDesign | None:
    """Step 1: Find house design by brand + name."""
    stmt = select(HouseDesign).where(
        HouseDesign.brand == brand,
        HouseDesign.house_name == house_name,
        HouseDesign.active.is_(True),
    )
    return db.execute(stmt).scalars().first()


def _lookup_facade(db: Session, design_id: int, facade_name: str) -> HouseFacade | None:
    """Step 2: Find facade for a house design."""
    stmt = select(HouseFacade).where(
        HouseFacade.design_id == design_id,
        HouseFacade.facade_name == facade_name,
    )
    return db.execute(stmt).scalars().first()


def _lookup_energy_compliance(
    db: Session, design_id: int, garage_side: str, orientation: str
) -> Decimal:
    """Step 3: Energy compliance cost. Returns 0 if no rating found."""
    stmt = select(EnergyRating).where(
        EnergyRating.design_id == design_id,
        EnergyRating.garage_side == garage_side,
        EnergyRating.orientation == orientation,
    )
    rating = db.execute(stmt).scalars().first()
    if rating is None:
        return Decimal("0")
    return _dec(rating.compliance_cost)


def _get_size_band_cost(item: SiteCostItem, storey: str, gf_sqm: float) -> Decimal:
    """Pick the right cost column from a SiteCostItem based on storey and GF area."""
    is_single = storey.lower() == "single"
    sqm = gf_sqm

    if sqm < 190:
        cost = item.cost_single_lt190 if is_single else item.cost_double_lt190
    elif sqm <= 249:
        cost = item.cost_single_191_249 if is_single else item.cost_double_191_249
    elif sqm <= 300:
        cost = item.cost_single_250_300 if is_single else item.cost_double_250_300
    else:
        cost = item.cost_single_300plus if is_single else item.cost_double_300plus

    return _dec(cost)


def _condition_matches(condition_type: str | None, lot_input: LotPricingInput) -> bool:
    """Check if a site cost item's condition matches the lot input."""
    if condition_type is None or condition_type == "always":
        return True
    ct = condition_type.lower().strip()
    if ct == "corner_block":
        return lot_input.corner_block
    if ct == "fill_trees":
        return lot_input.fill_trees
    if ct == "easement_proximity_lhs":
        return lot_input.easement_proximity_lhs
    if ct == "easement_proximity_rhs":
        return lot_input.easement_proximity_rhs
    if ct == "retaining_lhs":
        return lot_input.retaining_lhs
    if ct == "retaining_rhs":
        return lot_input.retaining_rhs
    if ct == "fall_gt_300":
        return lot_input.fall_mm > 300
    # Default: include (treat unknown conditions as always)
    return True


def _calculate_site_costs(
    db: Session,
    lot_input: LotPricingInput,
    house: HouseDesign,
    postcode: str,
) -> tuple[Decimal, list[dict]]:
    """Step 4: Site costs from tier matrix + postcode rock removal.

    1. Always include base items (tier_id IS NULL).
    2. Find the tier matching fall_mm and include tiered items.
    3. Add postcode rock removal if applicable.
    """
    total = Decimal("0")
    items: list[dict] = []

    # Base items (always applied)
    base_items_stmt = (
        select(SiteCostItem)
        .where(SiteCostItem.tier_id.is_(None))
        .order_by(SiteCostItem.sort_order)
    )
    base_items = list(db.execute(base_items_stmt).scalars().all())

    for item in base_items:
        if _condition_matches(item.condition_type, lot_input):
            cost = _get_size_band_cost(item, house.storey, house.gf_sqm)
            if cost > 0:
                total += cost
                items.append({
                    "name": item.item_name,
                    "cost": cost,
                    "condition": item.condition_type,
                })

    # Tiered items based on fall
    if lot_input.fall_mm > 0:
        tier_stmt = select(SiteCostTier).where(
            SiteCostTier.fall_min_mm <= lot_input.fall_mm,
            SiteCostTier.fall_max_mm >= lot_input.fall_mm,
        )
        tier = db.execute(tier_stmt).scalars().first()
        if tier:
            tier_items_stmt = (
                select(SiteCostItem)
                .where(SiteCostItem.tier_id == tier.tier_id)
                .order_by(SiteCostItem.sort_order)
            )
            tier_items = list(db.execute(tier_items_stmt).scalars().all())
            for item in tier_items:
                if _condition_matches(item.condition_type, lot_input):
                    cost = _get_size_band_cost(item, house.storey, house.gf_sqm)
                    if cost > 0:
                        total += cost
                        items.append({
                            "name": item.item_name,
                            "cost": cost,
                            "condition": item.condition_type,
                        })

    # Postcode rock removal
    postcode_cost = db.get(PostcodeSiteCost, postcode)
    if postcode_cost and _dec(postcode_cost.rock_removal_cost) > 0:
        rock_cost = _dec(postcode_cost.rock_removal_cost)
        total += rock_cost
        items.append({
            "name": f"Rock Removal (postcode {postcode})",
            "cost": rock_cost,
            "condition": "postcode",
        })

    return total, items


def _calculate_design_guidelines(
    db: Session,
    estate_id: int,
    stage_id: int,
    has_corner: bool,
) -> tuple[Decimal, list[dict]]:
    """Step 5: Sum estate design guideline costs."""
    from sqlalchemy import or_

    stmt = (
        select(EstateDesignGuideline)
        .where(
            EstateDesignGuideline.estate_id == estate_id,
            or_(
                EstateDesignGuideline.stage_id == stage_id,
                EstateDesignGuideline.stage_id.is_(None),
            ),
        )
    )
    guidelines = list(db.execute(stmt).scalars().all())

    total = Decimal("0")
    items: list[dict] = []
    for g in guidelines:
        if g.cost is not None:
            cost = _dec(g.cost)
            total += cost
            # Use override_text if available, otherwise type_id reference
            name = g.override_text or f"Guideline #{g.type_id}"
            items.append({"name": name, "cost": cost})

    if not has_corner and total > 0:
        savings = min(CORNER_BLOCK_SAVINGS, total)
        total -= savings
        items.append({"name": "No corner block savings", "cost": -savings})

    return total, items


def _calculate_upgrades(
    db: Session,
    context: PricingContext,
    house: HouseDesign,
    facade: HouseFacade | None,
) -> tuple[Decimal, list[dict]]:
    """Step 7: Sum applicable upgrades for the brand."""
    stmt = (
        select(UpgradeItem)
        .where(UpgradeItem.brand == context.brand)
        .order_by(UpgradeItem.sort_order)
    )
    all_upgrades = list(db.execute(stmt).scalars().all())

    total = Decimal("0")
    items: list[dict] = []
    is_hps = "HPS" in house.house_name.upper()

    for i, upgrade in enumerate(all_upgrades):
        cost = _dec(upgrade.price)

        # Skip HPS-specific upgrades for non-HPS houses
        cat_name = ""
        if upgrade.category is not None:
            cat_name = upgrade.category.name if hasattr(upgrade.category, "name") else ""
        if not is_hps and "HPS" in (upgrade.description.upper() if upgrade.description else ""):
            continue

        # Skip facade neutralizing (first upgrade) for neutralizing facades
        if i == 0 and facade and facade.facade_name in NEUTRALIZING_FACADES:
            continue

        total += cost
        items.append({"description": upgrade.description, "cost": cost})

    return total, items


def _calculate_discount(
    lot_size: Decimal,
    suburb: str,
    postcode: str,
    wholesale_group: str | None,
) -> tuple[Decimal, str | None]:
    """Step 8: Location and size-based discounts.

    Rules (additive):
    - $5,000 if lot_size < 300 sqm OR postcode in Latrobe Valley
    - $3,000 if wholesale_group == 'Dwellings Property Group'
    """
    total = Decimal("0")
    reasons: list[str] = []

    if lot_size < SMALL_LOT_THRESHOLD or postcode in LATROBE_VALLEY_POSTCODES:
        total += SMALL_LOT_DISCOUNT
        if lot_size < SMALL_LOT_THRESHOLD:
            reasons.append(f"Small lot (<{SMALL_LOT_THRESHOLD}m\u00b2)")
        if postcode in LATROBE_VALLEY_POSTCODES:
            reasons.append("Latrobe Valley postcode")

    if wholesale_group and wholesale_group.strip().lower() == "dwellings property group":
        total += DWELLINGS_DISCOUNT
        reasons.append("Dwellings Property Group")

    reason = "; ".join(reasons) if reasons else None
    return total, reason


def _lookup_commission(
    db: Session,
    bdm_profile_id: int | None,
    wholesale_group_name: str | None,
    brand: str,
) -> tuple[Decimal | None, Decimal | None]:
    """Step 9: Commission lookup.

    Returns (fixed_amount, pct_rate) -- one will be None.
    If no BDM or wholesale group, return (BASE_COMMISSION, None).
    """
    if bdm_profile_id is None or wholesale_group_name is None:
        return BASE_COMMISSION, None

    # Resolve wholesale group
    group = db.execute(
        select(WholesaleGroup).where(WholesaleGroup.group_name == wholesale_group_name)
    ).scalars().first()
    if group is None:
        return BASE_COMMISSION, None

    stmt = select(CommissionRate).where(
        CommissionRate.bdm_profile_id == bdm_profile_id,
        CommissionRate.group_id == group.group_id,
    )
    rate = db.execute(stmt).scalars().first()
    if rate is None:
        return BASE_COMMISSION, None

    if rate.commission_fixed is not None:
        return _dec(rate.commission_fixed), None
    if rate.commission_pct is not None:
        return None, _dec(rate.commission_pct)

    return BASE_COMMISSION, None


def _calculate_fbc_escalation(
    db: Session,
    brand: str,
    pricing_date: date,
    contract_date: date,
    base_amount: Decimal,
) -> tuple[Decimal, Decimal]:
    """Step 10: Future Build Cost escalation.

    Calculate days between pricing_date and contract_date.
    Look up FBC band for that number of days.
    Return (percentage, dollar_amount).
    """
    days_diff = (contract_date - pricing_date).days
    if days_diff <= 30:
        return Decimal("0"), Decimal("0")

    stmt = select(FbcEscalationBand).where(
        FbcEscalationBand.brand == brand,
        FbcEscalationBand.day_start <= days_diff,
        FbcEscalationBand.day_end >= days_diff,
    )
    band = db.execute(stmt).scalars().first()
    if band is None:
        # If beyond all bands, use the last band
        stmt_last = (
            select(FbcEscalationBand)
            .where(FbcEscalationBand.brand == brand)
            .order_by(FbcEscalationBand.day_end.desc())
            .limit(1)
        )
        band = db.execute(stmt_last).scalars().first()
        if band is None:
            return Decimal("0"), Decimal("0")

    # multiplier is e.g. 1.003 meaning 0.3% escalation
    pct = _dec(band.multiplier) - Decimal("1")
    # FBC applies to base_amount (house + facade + landscaping + upgrades - guidelines - 33000)
    amount = (base_amount * pct + Decimal("1000")).quantize(Decimal("1"), rounding=ROUND_UP)
    return pct * Decimal("100"), amount  # Return pct as percentage (e.g., 0.3)


def _assemble_build_price(breakdown: PriceBreakdown) -> Decimal:
    """Step 11: Total Build Price with commission netting and rounding.

    Components = house + facade + energy + site_costs + guidelines + landscaping
                 + upgrades - discount + kdrb + fbc

    If fixed commission:
        build = ROUNDUP(components - guidelines - (BASE_COMMISSION - commission_fixed + comms_adj), -2)
                + guidelines
    If percentage commission:
        build = ROUNDUP(components - guidelines - BASE_COMMISSION + comms_adj, -2)
                + guidelines
    """
    components = (
        breakdown.house_price
        + breakdown.facade_price
        + breakdown.energy_compliance_cost
        + breakdown.site_costs_total
        + breakdown.design_guidelines_total
        + breakdown.extra_landscaping
        + breakdown.upgrades_total
        - breakdown.discount
        + breakdown.kdrb_surcharge
        + breakdown.fbc_escalation_amount
    )

    guidelines = breakdown.design_guidelines_total

    if breakdown.commission_fixed is not None:
        net = (
            components
            - guidelines
            - (BASE_COMMISSION - breakdown.commission_fixed + breakdown.comms_adjustment)
        )
        build = _round_up_100(net) + guidelines
    elif breakdown.commission_pct is not None:
        net = (
            components
            - guidelines
            - BASE_COMMISSION
            + breakdown.comms_adjustment
        )
        build = _round_up_100(net) + guidelines
    else:
        # No commission info -- use fixed with base
        net = components - guidelines
        build = _round_up_100(net) + guidelines

    return build


def _assemble_package_price(breakdown: PriceBreakdown) -> Decimal:
    """Step 12: Total Package Price.

    If fixed commission:
        package = land + build
    If percentage commission:
        package = ROUNDUP((land + build) / PCT_COMMISSION_DIVISOR, -2)
    """
    if breakdown.commission_pct is not None:
        raw = (breakdown.land_price + breakdown.total_build_price) / PCT_COMMISSION_DIVISOR
        return _round_up_100(raw)
    return breakdown.land_price + breakdown.total_build_price


def _check_house_fits(
    lot_input: LotPricingInput, house: HouseDesign
) -> tuple[bool, str | None]:
    """Check if lot dimensions accommodate the house."""
    house_frontage = _dec(house.frontage)
    house_depth = _dec(house.depth)

    if lot_input.lot_frontage < house_frontage:
        return False, f"Lot frontage {lot_input.lot_frontage}m < house min {house_frontage}m"
    if lot_input.lot_depth < house_depth:
        return False, f"Lot depth {lot_input.lot_depth}m < house min {house_depth}m"
    return True, None


def _calculate_extra_fence(lot_input: LotPricingInput, house: HouseDesign) -> Decimal:
    """Extra fence meterage = (lot_frontage - house_frontage) + 2*(lot_depth - house_depth)."""
    frontage_diff = lot_input.lot_frontage - _dec(house.frontage)
    depth_diff = lot_input.lot_depth - _dec(house.depth)
    extra = frontage_diff + Decimal("2") * depth_diff
    return max(Decimal("0"), extra)


# ---------------------------------------------------------------------------
# Main entry points
# ---------------------------------------------------------------------------
def calculate_lot_price(
    db: Session,
    context: PricingContext,
    lot_input: LotPricingInput,
    has_corner_in_batch: bool = False,
) -> PriceBreakdown:
    """Complete pricing calculation for a single lot.

    Steps (matching Excel Pricing Sheet formulas):
    1. House Price -- lookup from house_designs
    2. Facade Price -- lookup from house_facades
    3. Energy Compliance -- lookup from energy_ratings
    4. Site Costs -- calculate from site_cost_matrix + postcode_site_costs
    5. Design Guidelines -- sum estate_design_guidelines for the estate
    6. Extra Landscaping -- max(0, lot_size - house_lot_total) * $39/sqm
    7. Upgrades -- sum applicable upgrade_items
    8. Discounts -- location/size/wholesale group based
    9. Commission -- lookup from commission_rates
    10. FBC Escalation -- 0.3% per 30-day period
    11. Total Build Price -- assemble with rounding to nearest $100
    12. Total Package Price -- land + build (adjusted for commission type)
    13. Holding Costs -- 10% of build (if applicable)
    Also: House Fits check, Extra Fence Meterage calculation
    """
    breakdown = PriceBreakdown(
        lot_number=lot_input.lot_number,
        house_name=lot_input.house_name,
        facade_name=lot_input.facade_name,
        land_price=lot_input.land_price,
    )

    # Step 1: House Price
    house = _lookup_house(db, context.brand, lot_input.house_name)
    if not house:
        breakdown.warnings.append(f"House '{lot_input.house_name}' not found in catalog")
        return breakdown
    breakdown.house_price = _dec(house.base_price)
    breakdown.line_items.append(
        PriceLineItem("House Base Price", breakdown.house_price, "house", house.house_name)
    )

    # Step 2: Facade Price
    facade = _lookup_facade(db, house.design_id, lot_input.facade_name)
    if facade:
        breakdown.facade_price = _dec(facade.facade_price)
        breakdown.line_items.append(
            PriceLineItem("Facade", breakdown.facade_price, "facade", facade.facade_name)
        )
    else:
        breakdown.warnings.append(
            f"Facade '{lot_input.facade_name}' not found for house '{lot_input.house_name}'"
        )

    # Step 3: Energy Compliance
    breakdown.energy_compliance_cost = _lookup_energy_compliance(
        db, house.design_id, lot_input.garage_side, lot_input.orientation
    )
    if breakdown.energy_compliance_cost > 0:
        breakdown.line_items.append(
            PriceLineItem("Energy Compliance", breakdown.energy_compliance_cost, "energy")
        )

    # Step 4: Site Costs
    breakdown.site_costs_total, site_items = _calculate_site_costs(
        db, lot_input, house, context.postcode
    )
    for item in site_items:
        breakdown.line_items.append(
            PriceLineItem(item["name"], item["cost"], "site_cost", item.get("condition"))
        )

    # Step 5: Design Guidelines
    breakdown.design_guidelines_total, guideline_items = _calculate_design_guidelines(
        db, context.estate_id, context.stage_id, has_corner_in_batch
    )
    for item in guideline_items:
        breakdown.line_items.append(
            PriceLineItem(item["name"], item["cost"], "guideline")
        )

    # Step 6: Extra Landscaping
    house_lot_total = _dec(house.lot_total_sqm)
    breakdown.extra_landscaping_sqm = max(Decimal("0"), lot_input.lot_size_sqm - house_lot_total)
    breakdown.extra_landscaping = breakdown.extra_landscaping_sqm * LANDSCAPING_RATE_PER_SQM
    if breakdown.extra_landscaping > 0:
        breakdown.line_items.append(
            PriceLineItem(
                "Extra Landscaping",
                breakdown.extra_landscaping,
                "landscaping",
                f"{breakdown.extra_landscaping_sqm}m\u00b2 \u00d7 ${LANDSCAPING_RATE_PER_SQM}/m\u00b2",
            )
        )

    # Step 7: Upgrades
    breakdown.upgrades_total, upgrade_items = _calculate_upgrades(db, context, house, facade)
    for item in upgrade_items:
        breakdown.line_items.append(
            PriceLineItem(item["description"], item["cost"], "upgrade")
        )

    # Step 8: Discounts
    breakdown.discount, breakdown.discount_reason = _calculate_discount(
        lot_input.lot_size_sqm, context.suburb, context.postcode, context.wholesale_group_name
    )
    if breakdown.discount > 0:
        breakdown.line_items.append(
            PriceLineItem("Discount", -breakdown.discount, "discount", breakdown.discount_reason)
        )

    # Step 9: KDRB Surcharge
    if context.is_kdrb:
        breakdown.kdrb_surcharge = KDRB_SURCHARGE
        breakdown.line_items.append(
            PriceLineItem("KDRB Surcharge", KDRB_SURCHARGE, "kdrb")
        )

    # Step 10: Commission
    breakdown.commission_fixed, breakdown.commission_pct = _lookup_commission(
        db, context.bdm_profile_id, context.wholesale_group_name, context.brand
    )

    # Step 11: FBC Escalation
    if context.contract_date and context.pricing_date:
        breakdown.fbc_escalation_pct, breakdown.fbc_escalation_amount = _calculate_fbc_escalation(
            db,
            context.brand,
            context.pricing_date,
            context.contract_date,
            breakdown.house_price,  # Escalation applies to house base price
        )
        if breakdown.fbc_escalation_amount > 0:
            breakdown.line_items.append(
                PriceLineItem(
                    "FBC Escalation",
                    breakdown.fbc_escalation_amount,
                    "fbc",
                    f"{breakdown.fbc_escalation_pct}%",
                )
            )

    # Step 12: Total Build Price
    breakdown.total_build_price = _assemble_build_price(breakdown)

    # Step 13: Total Package Price
    breakdown.total_package_price = _assemble_package_price(breakdown)

    # Step 14: Holding Costs
    if context.is_10_90_deal and context.holding_costs_apply:
        breakdown.holding_costs = (breakdown.total_build_price * HOLDING_COST_RATE).quantize(
            Decimal("1"), ROUND_UP
        )
        breakdown.line_items.append(
            PriceLineItem("10% Holding Costs", breakdown.holding_costs, "holding")
        )

    # Validation: House Fits?
    breakdown.house_fits, breakdown.house_fits_reason = _check_house_fits(lot_input, house)

    # Extra Fence Meterage
    breakdown.extra_fence_meterage = _calculate_extra_fence(lot_input, house)

    return breakdown


def calculate_batch(
    db: Session,
    context: PricingContext,
    lots: list[LotPricingInput],
) -> list[PriceBreakdown]:
    """Calculate prices for a batch of lots (one pricing request).

    Corner block logic: if ANY lot in batch is corner, all get full guidelines.
    If NO lots are corner, guidelines total gets reduced by CORNER_BLOCK_SAVINGS.
    """
    has_corner = any(lot.corner_block for lot in lots)
    return [calculate_lot_price(db, context, lot, has_corner) for lot in lots]

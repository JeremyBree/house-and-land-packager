"""One-time seed: import pricing reference data from the 2026 workbook.

Usage:
    python -m hlp.seeds.seed_pricing_data

This imports house designs, facades, energy ratings, upgrades, commissions,
travel surcharges, site costs, postcode costs, FBC bands, guideline types,
and estate guidelines from the Reference/Pricing sheet 2026.xlsm workbook.

Idempotent — existing records are skipped.
"""

import logging
import os
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)


def seed_pricing(db_session, workbook_path: str, brand: str = "Hermitage Homes"):
    """Run the pricing workbook import and log results."""
    from hlp.seeds.import_pricing_workbook import import_from_excel

    logger.info("Importing pricing data from: %s (brand: %s)", workbook_path, brand)
    result = import_from_excel(db_session, workbook_path, brand)
    db_session.commit()

    logger.info("=== Import Results ===")
    logger.info("  House designs created:    %d", result.houses_created)
    logger.info("  Facades created:          %d", result.facades_created)
    logger.info("  Energy ratings created:   %d", result.energy_ratings_created)
    logger.info("  Upgrade categories:       %d", result.upgrade_categories_created)
    logger.info("  Upgrade items:            %d", result.upgrades_created)
    logger.info("  Wholesale groups:         %d", result.wholesale_groups_created)
    logger.info("  Commission rates:         %d", result.commission_rates_created)
    logger.info("  Travel surcharges:        %d", result.travel_surcharges_created)
    logger.info("  Postcode costs:           %d", result.postcode_costs_created)
    logger.info("  Guideline types:          %d", result.guideline_types_created)
    logger.info("  Estate guidelines:        %d", result.estate_guidelines_created)
    logger.info("  FBC bands:                %d", result.fbc_bands_created)
    logger.info("  Site cost tiers:          %d", result.site_cost_tiers_created)
    logger.info("  Site cost items:          %d", result.site_cost_items_created)
    logger.info("  Skipped (existing):       %d", result.skipped)
    if result.errors:
        logger.warning("  Errors: %d", len(result.errors))
        for err in result.errors:
            logger.warning("    - %s", err)
    else:
        logger.info("  Errors: 0")

    return result


def main():
    # Find the workbook
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, "..", "..", ".."))
    workbook_path = os.path.join(project_root, "Reference", "Pricing sheet 2026.xlsm")

    if not os.path.exists(workbook_path):
        logger.error("Workbook not found at: %s", workbook_path)
        sys.exit(1)

    # Connect to database
    from hlp.database import get_session_factory

    session = get_session_factory()()
    try:
        seed_pricing(session, workbook_path)
    except Exception:
        session.rollback()
        logger.exception("Import failed")
        sys.exit(1)
    finally:
        session.close()

    logger.info("Pricing data seed complete.")


if __name__ == "__main__":
    main()

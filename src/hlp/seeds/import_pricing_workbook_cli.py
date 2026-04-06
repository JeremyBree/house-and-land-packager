"""CLI entry point: python -m hlp.seeds.import_pricing_workbook <path>"""

import sys

from hlp.database import get_session_factory
from hlp.seeds.import_pricing_workbook import import_from_excel


def main():
    if len(sys.argv) < 2:
        print("Usage: python -m hlp.seeds.import_pricing_workbook <path_to_xlsm> [brand]")
        sys.exit(1)

    path = sys.argv[1]
    brand = sys.argv[2] if len(sys.argv) > 2 else "Hermitage Homes"

    session = get_session_factory()()
    try:
        result = import_from_excel(session, path, brand)
        session.commit()
        print("\nImport complete:")
        for field_name, count in vars(result).items():
            if isinstance(count, int):
                print(f"  {field_name}: {count}")
        if result.errors:
            print(f"\nErrors ({len(result.errors)}):")
            for e in result.errors[:20]:
                print(f"  {e}")
    except Exception as e:
        session.rollback()
        print(f"Import failed: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()

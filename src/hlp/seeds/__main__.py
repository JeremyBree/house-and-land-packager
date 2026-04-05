"""`python -m hlp.seeds` — run dev seed."""

import logging
import sys

from hlp.database import Base, get_engine, get_session_factory
from hlp.seeds.dev_seed import seed_dev

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)


def main() -> None:
    logger.info("Ensuring tables exist...")
    Base.metadata.create_all(get_engine())

    factory = get_session_factory()
    session = factory()
    try:
        logger.info("Seeding dev data...")
        seed_dev(session)
        session.commit()
        logger.info("Seed complete.")
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()

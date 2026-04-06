"""Enum types used across models.

The `pg_*` Enum type instances are defined here once so SQLAlchemy reuses
the same PostgreSQL type across multiple columns/models (avoiding duplicate
CREATE TYPE statements).
"""

import enum

from sqlalchemy import Enum


class LotStatus(str, enum.Enum):
    AVAILABLE = "Available"
    UNAVAILABLE = "Unavailable"
    HOLD = "Hold"
    DEPOSIT_TAKEN = "Deposit Taken"
    SOLD = "Sold"


class StageStatus(str, enum.Enum):
    ACTIVE = "Active"
    UPCOMING = "Upcoming"
    COMPLETED = "Completed"


class Source(str, enum.Enum):
    EMAIL = "email"
    PORTAL = "portal"
    WEBSITE = "website"
    PDF = "pdf"
    MANUAL = "manual"


class Brand(str, enum.Enum):
    HERMITAGE = "Hermitage Homes"
    KINGSBRIDGE = "Kingsbridge Homes"


class PricingRequestStatus(str, enum.Enum):
    PENDING = "Pending"
    ESTIMATING = "Estimating"
    PRICED = "Priced"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"


class AgentType(str, enum.Enum):
    EMAIL = "email"
    SCRAPER = "scraper"
    PORTAL = "portal"
    PDF = "pdf"


class IngestionStatus(str, enum.Enum):
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"


class ConfigType(str, enum.Enum):
    EMAIL_ACCOUNT = "email_account"
    WEBSITE = "website"
    PORTAL = "portal"
    PDF_FOLDER = "pdf_folder"


class UserRoleType(str, enum.Enum):
    ADMIN = "admin"
    PRICING = "pricing"
    SALES = "sales"
    REQUESTER = "requester"
    BDM = "bdm"


# Shared SQLAlchemy Enum type instances — reuse these across models to avoid
# duplicate PostgreSQL type creation.
pg_lot_status = Enum(LotStatus, name="lot_status", create_type=True)
pg_stage_status = Enum(StageStatus, name="stage_status", create_type=True)
pg_source = Enum(Source, name="source_type", create_type=True)
pg_pricing_request_status = Enum(PricingRequestStatus, name="pricing_request_status", create_type=True)
pg_agent_type = Enum(AgentType, name="agent_type", create_type=True)
pg_ingestion_status = Enum(IngestionStatus, name="ingestion_status", create_type=True)
pg_config_type = Enum(ConfigType, name="config_type", create_type=True)
pg_user_role_type = Enum(UserRoleType, name="user_role_type", create_type=True)

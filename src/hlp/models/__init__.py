"""SQLAlchemy ORM models — import all so Base.metadata discovers them."""

from hlp.models.clash_rule import ClashRule
from hlp.models.configuration import Configuration
from hlp.models.developer import Developer
from hlp.models.estate import Estate
from hlp.models.estate_document import EstateDocument
from hlp.models.estate_stage import EstateStage
from hlp.models.house_package import HousePackage
from hlp.models.ingestion_log import IngestionLog
from hlp.models.notification import Notification
from hlp.models.pricing_request import PricingRequest
from hlp.models.pricing_rule import GlobalPricingRule, StagePricingRule
from hlp.models.pricing_rule_category import PricingRuleCategory
from hlp.models.pricing_template import PricingTemplate
from hlp.models.profile import Profile
from hlp.models.region import Region
from hlp.models.stage_lot import StageLot
from hlp.models.status_history import StatusHistory
from hlp.models.user_role import UserRole

__all__ = [
    "ClashRule",
    "Configuration",
    "Developer",
    "Estate",
    "EstateDocument",
    "EstateStage",
    "GlobalPricingRule",
    "HousePackage",
    "IngestionLog",
    "Notification",
    "PricingRequest",
    "PricingRuleCategory",
    "PricingTemplate",
    "Profile",
    "Region",
    "StageLot",
    "StagePricingRule",
    "StatusHistory",
    "UserRole",
]

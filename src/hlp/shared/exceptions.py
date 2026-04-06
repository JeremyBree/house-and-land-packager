"""Custom exception types raised by service/repository layers."""


class HLPError(Exception):
    """Base class for all application-specific errors."""


class AuthenticationError(HLPError):
    """Raised when authentication fails (bad credentials, missing token, etc.)."""


class NotAuthorizedError(HLPError):
    """Raised when the authenticated user is not permitted to perform an action."""


class DuplicateEmailError(HLPError):
    """Raised when attempting to create a user with an email that already exists."""


class UserNotFoundError(HLPError):
    """Raised when a user lookup fails."""


class MinRolesRequiredError(HLPError):
    """Raised when attempting to assign fewer than the required minimum roles."""


class NotFoundError(HLPError):
    """Generic entity-not-found error."""


class InvalidStatusTransitionError(HLPError):
    """Raised when a lot status transition is not allowed."""


class InvalidCsvError(HLPError):
    """Raised when a CSV upload cannot be parsed."""


class UnsupportedFileTypeError(HLPError):
    """Raised when an uploaded file's type is not allowed."""


class FileTooLargeError(HLPError):
    """Raised when an uploaded file exceeds the allowed size."""


class StageNotFoundError(NotFoundError):
    """Raised when a stage lookup fails."""


class LotNotFoundError(NotFoundError):
    """Raised when a lot lookup fails."""


class DocumentNotFoundError(NotFoundError):
    """Raised when a document lookup fails."""


class ExportTooLargeError(HLPError):
    """Raised when an export request would exceed the maximum allowed rows."""


class FilterPresetNotFoundError(NotFoundError):
    """Raised when a filter preset lookup fails (or does not belong to user)."""


class DuplicatePresetNameError(HLPError):
    """Raised when a user already has a filter preset with the same name."""


class ClashRuleNotFoundError(NotFoundError):
    """Raised when a clash rule lookup fails."""


class PackageNotFoundError(NotFoundError):
    """Raised when a house package lookup fails."""


class DuplicateClashRuleError(HLPError):
    """Raised when attempting to create a clash rule that already exists for the scope."""


class TemplateNotFoundError(NotFoundError):
    """Raised when a pricing template lookup fails."""


class InvalidTemplateError(HLPError):
    """Raised when an uploaded pricing template is invalid (bad format, etc.)."""


class PricingRuleNotFoundError(NotFoundError):
    """Raised when a pricing rule lookup fails."""


class CategoryNotFoundError(NotFoundError):
    """Raised when a pricing rule category lookup fails."""

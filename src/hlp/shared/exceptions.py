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

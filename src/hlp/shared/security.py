"""Password hashing + JWT token utilities."""

from datetime import UTC, datetime, timedelta

from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from hlp.config import get_settings
from hlp.shared.exceptions import AuthenticationError

_settings = get_settings()

_pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=_settings.bcrypt_rounds,
)


class TokenPayload(BaseModel):
    """Decoded JWT payload."""

    sub: int
    email: str
    roles: list[str]
    exp: datetime


def hash_password(plain: str) -> str:
    """Hash a plain text password using bcrypt."""
    return _pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    """Return True iff the plain password matches the bcrypt hash."""
    try:
        return _pwd_context.verify(plain, hashed)
    except Exception:
        return False


def create_access_token(subject: int, roles: list[str], email: str) -> str:
    """Create a signed JWT access token for the given profile."""
    settings = get_settings()
    now = datetime.now(UTC)
    expire = now + timedelta(minutes=settings.jwt_expire_minutes)
    payload = {
        "sub": str(subject),
        "email": email,
        "roles": roles,
        "exp": expire,
        "iat": now,
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> TokenPayload:
    """Decode and validate a JWT. Raises AuthenticationError on failure."""
    settings = get_settings()
    try:
        raw = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except JWTError as exc:
        raise AuthenticationError(f"Invalid or expired token: {exc}") from exc

    try:
        sub = int(raw["sub"])
        email = raw["email"]
        roles = list(raw.get("roles", []))
        exp = datetime.fromtimestamp(raw["exp"], tz=UTC)
    except (KeyError, TypeError, ValueError) as exc:
        raise AuthenticationError(f"Malformed token payload: {exc}") from exc

    return TokenPayload(sub=sub, email=email, roles=roles, exp=exp)

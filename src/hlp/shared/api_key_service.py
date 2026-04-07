"""API key generation, verification, and management."""

import secrets
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from hlp.models.api_key import ApiKey
from hlp.shared.security import hash_password, verify_password


def generate_api_key() -> tuple[str, str, str]:
    """Generate a random API key. Returns (raw_key, key_hash, key_prefix)."""
    raw_key = "hlp_" + secrets.token_urlsafe(36)
    key_hash = hash_password(raw_key)
    key_prefix = raw_key[:8]
    return raw_key, key_hash, key_prefix


def verify_api_key(db: Session, raw_key: str) -> ApiKey | None:
    """Look up an API key by prefix, verify hash, check expiry. Updates last_used_at."""
    key_prefix = raw_key[:8]
    stmt = select(ApiKey).where(ApiKey.key_prefix == key_prefix, ApiKey.is_active.is_(True))
    candidates = list(db.execute(stmt).scalars().all())

    for candidate in candidates:
        if not verify_password(raw_key, candidate.key_hash):
            continue
        # Check expiry
        if candidate.expires_at is not None:
            if datetime.now(UTC) > candidate.expires_at:
                return None
        candidate.last_used_at = datetime.now(UTC)
        db.flush()
        return candidate

    return None


def create_api_key(
    db: Session,
    agent_name: str,
    agent_type: str,
    scopes: str,
    created_by: int,
    expires_at: datetime | None = None,
    notes: str | None = None,
) -> tuple[ApiKey, str]:
    """Generate and persist a new API key. Returns (ApiKey, raw_key). Raw key is shown once only."""
    raw_key, key_hash, key_prefix = generate_api_key()
    api_key = ApiKey(
        key_hash=key_hash,
        key_prefix=key_prefix,
        agent_name=agent_name,
        agent_type=agent_type,
        scopes=scopes,
        created_by=created_by,
        expires_at=expires_at,
        notes=notes,
    )
    db.add(api_key)
    db.flush()
    return api_key, raw_key


def revoke_api_key(db: Session, key_id: int) -> ApiKey | None:
    """Revoke an API key by setting is_active = False."""
    api_key = db.get(ApiKey, key_id)
    if api_key is None:
        return None
    api_key.is_active = False
    db.flush()
    return api_key


def list_api_keys(db: Session) -> list[ApiKey]:
    """Return all API keys (caller must exclude hash from responses)."""
    stmt = select(ApiKey).order_by(ApiKey.created_at.desc())
    return list(db.execute(stmt).scalars().all())

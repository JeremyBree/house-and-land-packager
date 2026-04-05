"""Unit tests for hlp.shared.security (bcrypt + JWT)."""
from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from jose import jwt

from hlp.config import get_settings
from hlp.shared.exceptions import AuthenticationError
from hlp.shared.security import (
    TokenPayload,
    create_access_token,
    decode_token,
    hash_password,
    verify_password,
)


def test_hash_password_produces_different_hashes_for_same_input():
    h1 = hash_password("secret-123")
    h2 = hash_password("secret-123")
    assert h1 != h2  # bcrypt salt varies
    assert h1.startswith("$2")


def test_verify_password_accepts_correct():
    hashed = hash_password("correct-horse")
    assert verify_password("correct-horse", hashed) is True


def test_verify_password_rejects_wrong():
    hashed = hash_password("correct-horse")
    assert verify_password("wrong-horse", hashed) is False


def test_verify_password_rejects_invalid_hash_format():
    # Garbage hash should return False (not raise).
    assert verify_password("anything", "not-a-valid-bcrypt-hash") is False
    assert verify_password("anything", "") is False


def test_create_and_decode_token_roundtrip():
    token = create_access_token(subject=42, roles=["admin", "pricing"], email="a@b.test")
    payload = decode_token(token)
    assert isinstance(payload, TokenPayload)
    assert payload.sub == 42
    assert payload.email == "a@b.test"
    assert payload.roles == ["admin", "pricing"]
    assert payload.exp > datetime.now(UTC)


def test_decode_token_raises_on_tampered_signature():
    token = create_access_token(subject=1, roles=["admin"], email="a@b.test")
    tampered = token[:-4] + ("AAAA" if token[-4:] != "AAAA" else "BBBB")
    with pytest.raises(AuthenticationError):
        decode_token(tampered)


def test_decode_token_raises_on_expired():
    # Build a manually expired token using the real secret/alg.
    settings = get_settings()
    now = datetime.now(UTC)
    payload = {
        "sub": "7",
        "email": "x@y.test",
        "roles": ["admin"],
        "exp": now - timedelta(minutes=5),
        "iat": now - timedelta(minutes=10),
    }
    expired = jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    with pytest.raises(AuthenticationError):
        decode_token(expired)


def test_decode_token_raises_on_missing_claims():
    settings = get_settings()
    # No email, no sub.
    bad = jwt.encode(
        {"exp": datetime.now(UTC) + timedelta(minutes=10)},
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )
    with pytest.raises(AuthenticationError):
        decode_token(bad)


def test_token_contains_expected_claims():
    token = create_access_token(subject=9, roles=["sales"], email="s@t.test")
    settings = get_settings()
    raw = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    assert raw["sub"] == "9"  # stored as str for JWT compatibility
    assert raw["email"] == "s@t.test"
    assert raw["roles"] == ["sales"]
    assert "exp" in raw
    assert "iat" in raw

    payload = decode_token(token)
    assert isinstance(payload.sub, int)
    assert isinstance(payload.email, str)
    assert isinstance(payload.roles, list)
    assert isinstance(payload.exp, datetime)

"""Unit tests for hlp.shared.auth_service (uses in-memory SQLite via conftest)."""
from __future__ import annotations

import pytest

from hlp.models.enums import UserRoleType
from hlp.shared import auth_service, user_service
from hlp.shared.exceptions import AuthenticationError


def _make_user(db, *, email="user@test.com", password="Passw0rd!", roles=None):
    roles = roles or [UserRoleType.ADMIN]
    return user_service.create_user_with_roles(
        db,
        email=email,
        password=password,
        first_name="Test",
        last_name="User",
        job_title="Tester",
        roles=roles,
    )


def test_authenticate_valid_credentials(db_session):
    _make_user(db_session, email="alice@test.com", password="Alice1234!")

    profile = auth_service.authenticate(db_session, "alice@test.com", "Alice1234!")

    assert profile.email == "alice@test.com"
    assert profile.first_name == "Test"
    assert len(profile.user_roles) == 1


def test_authenticate_is_case_insensitive_on_email(db_session):
    _make_user(db_session, email="mixed@test.com", password="Mixed1234!")
    profile = auth_service.authenticate(db_session, "MIXED@test.com", "Mixed1234!")
    assert profile.email == "mixed@test.com"


def test_authenticate_wrong_password_raises(db_session):
    _make_user(db_session, email="bob@test.com", password="Bob12345!")
    with pytest.raises(AuthenticationError):
        auth_service.authenticate(db_session, "bob@test.com", "wrong-pass")


def test_authenticate_unknown_email_raises(db_session):
    with pytest.raises(AuthenticationError):
        auth_service.authenticate(db_session, "nobody@test.com", "whatever")


def test_build_token_for_includes_roles(db_session):
    profile = _make_user(
        db_session,
        email="multi@test.com",
        password="Multi1234!",
        roles=[UserRoleType.ADMIN, UserRoleType.PRICING],
    )

    token_response = auth_service.build_token_for(profile)

    assert token_response.token_type == "bearer"
    assert token_response.access_token
    assert token_response.expires_in > 0

    # Decode and verify roles are in the token.
    from hlp.shared.security import decode_token

    payload = decode_token(token_response.access_token)
    assert payload.sub == profile.profile_id
    assert payload.email == profile.email
    assert set(payload.roles) == {"admin", "pricing"}

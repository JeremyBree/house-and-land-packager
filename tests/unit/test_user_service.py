"""Unit tests for hlp.shared.user_service."""
from __future__ import annotations

import pytest

from hlp.models.enums import UserRoleType
from hlp.repositories import profile_repository
from hlp.shared import user_service
from hlp.shared.exceptions import (
    DuplicateEmailError,
    MinRolesRequiredError,
    UserNotFoundError,
)


def _create(db, **overrides):
    fields = dict(
        email="user@test.com",
        password="Passw0rd!",
        first_name="First",
        last_name="Last",
        job_title="Tester",
        roles=[UserRoleType.SALES],
    )
    fields.update(overrides)
    return user_service.create_user_with_roles(db, **fields)


def test_create_user_hashes_password(db_session):
    profile = _create(db_session, email="hash@test.com", password="Plain1234!")
    assert profile.password_hash != "Plain1234!"
    assert profile.password_hash.startswith("$2")


def test_create_user_persists_profile_fields(db_session):
    profile = _create(
        db_session,
        email="fields@test.com",
        first_name="Alice",
        last_name="Smith",
        job_title="Engineer",
        roles=[UserRoleType.ADMIN, UserRoleType.PRICING],
    )
    assert profile.email == "fields@test.com"
    assert profile.first_name == "Alice"
    assert profile.last_name == "Smith"
    assert profile.job_title == "Engineer"
    assert profile.email_verified is False
    assert {ur.role for ur in profile.user_roles} == {
        UserRoleType.ADMIN,
        UserRoleType.PRICING,
    }


def test_create_user_with_duplicate_email_raises(db_session):
    _create(db_session, email="dup@test.com")
    with pytest.raises(DuplicateEmailError):
        _create(db_session, email="dup@test.com")


def test_create_user_without_roles_raises(db_session):
    with pytest.raises(MinRolesRequiredError):
        _create(db_session, email="noroles@test.com", roles=[])


def test_create_user_dedupes_roles(db_session):
    profile = _create(
        db_session,
        email="dedup@test.com",
        roles=[UserRoleType.SALES, UserRoleType.SALES, UserRoleType.REQUESTER],
    )
    assert {ur.role for ur in profile.user_roles} == {
        UserRoleType.SALES,
        UserRoleType.REQUESTER,
    }
    assert len(profile.user_roles) == 2


def test_set_user_roles_replaces_existing(db_session):
    profile = _create(db_session, email="roles@test.com", roles=[UserRoleType.SALES])
    assert [ur.role for ur in profile.user_roles] == [UserRoleType.SALES]

    user_service.set_user_roles(
        db_session,
        profile.profile_id,
        [UserRoleType.ADMIN, UserRoleType.PRICING],
    )

    # Re-fetch to verify persisted state.
    reloaded = profile_repository.get_by_id(db_session, profile.profile_id)
    assert reloaded is not None
    assert {ur.role for ur in reloaded.user_roles} == {
        UserRoleType.ADMIN,
        UserRoleType.PRICING,
    }


def test_set_user_roles_empty_list_raises(db_session):
    profile = _create(db_session, email="empty@test.com")
    with pytest.raises(MinRolesRequiredError):
        user_service.set_user_roles(db_session, profile.profile_id, [])


def test_set_user_roles_on_missing_profile_raises(db_session):
    with pytest.raises(UserNotFoundError):
        user_service.set_user_roles(db_session, 999_999, [UserRoleType.ADMIN])


def test_delete_user_removes_profile_and_roles(db_session):
    profile = _create(
        db_session,
        email="del@test.com",
        roles=[UserRoleType.ADMIN, UserRoleType.PRICING],
    )
    pid = profile.profile_id
    user_service.delete_user(db_session, pid)
    db_session.flush()

    assert profile_repository.get_by_id(db_session, pid) is None

    # Roles should be cascade-deleted.
    from hlp.models.user_role import UserRole
    remaining = db_session.query(UserRole).filter_by(profile_id=pid).all()
    assert remaining == []


def test_delete_user_missing_raises(db_session):
    with pytest.raises(UserNotFoundError):
        user_service.delete_user(db_session, 888_888)


def test_update_user_changes_only_specified_fields(db_session):
    profile = _create(
        db_session,
        email="upd@test.com",
        first_name="Orig",
        last_name="Name",
        job_title="Old Title",
    )
    original_email = profile.email

    updated = user_service.update_user(
        db_session,
        profile.profile_id,
        first_name="NewFirst",
        job_title="New Title",
    )
    assert updated.first_name == "NewFirst"
    assert updated.last_name == "Name"  # untouched
    assert updated.job_title == "New Title"
    assert updated.email == original_email


def test_update_user_ignores_none_values(db_session):
    profile = _create(db_session, email="none@test.com", first_name="Keep")
    user_service.update_user(
        db_session, profile.profile_id, first_name=None, last_name="Newer"
    )
    reloaded = profile_repository.get_by_id(db_session, profile.profile_id)
    assert reloaded is not None
    assert reloaded.first_name == "Keep"
    assert reloaded.last_name == "Newer"


def test_update_user_on_missing_profile_raises(db_session):
    with pytest.raises(UserNotFoundError):
        user_service.update_user(db_session, 777_777, first_name="Ghost")

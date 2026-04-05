"""Unit tests for hlp.shared.exceptions."""
from __future__ import annotations

import pytest

from hlp.shared.exceptions import (
    AuthenticationError,
    DuplicateEmailError,
    HLPError,
    MinRolesRequiredError,
    NotAuthorizedError,
    NotFoundError,
    UserNotFoundError,
)

ALL_CUSTOM_EXCEPTIONS = [
    AuthenticationError,
    NotAuthorizedError,
    DuplicateEmailError,
    UserNotFoundError,
    MinRolesRequiredError,
    NotFoundError,
]


@pytest.mark.parametrize("exc_cls", ALL_CUSTOM_EXCEPTIONS)
def test_custom_exception_is_subclass_of_hlperror(exc_cls):
    assert issubclass(exc_cls, HLPError)
    assert issubclass(exc_cls, Exception)


@pytest.mark.parametrize("exc_cls", ALL_CUSTOM_EXCEPTIONS)
def test_custom_exception_str_returns_message(exc_cls):
    msg = f"boom from {exc_cls.__name__}"
    exc = exc_cls(msg)
    assert str(exc) == msg


def test_hlp_error_is_exception():
    assert issubclass(HLPError, Exception)
    assert str(HLPError("hi")) == "hi"


def test_raising_and_catching_as_hlp_error():
    with pytest.raises(HLPError):
        raise DuplicateEmailError("already exists")

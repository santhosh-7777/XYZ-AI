from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

import backend.app.security.rbac as rbac


def make_credentials(token: str = "valid-token"):
    return HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials=token,
    )


class FakeDB:
    def __init__(self, user=None, role=None, permission=None):
        self.user = user
        self.role = role
        self.permission = permission

    def scalar(self, query):
        # The RBAC implementation uses scalar() for both
        # User and Permission queries.
        if self.user is not None:
            user = self.user
            self.user = None
            return user

        return self.permission

    def get(self, model, object_id):
        return self.role


def test_require_permission_returns_dependency():
    dependency = rbac.require_permission("OWN_ATTENDANCE")

    assert callable(dependency)


def test_permission_allowed_returns_user(monkeypatch):
    user = SimpleNamespace(
        id=1,
        role_id=10,
        is_active=True,
    )

    role = SimpleNamespace(
        id=10,
        name="STUDENT",
    )

    permission = SimpleNamespace(
        role_id=10,
        intent="OWN_ATTENDANCE",
        allowed=True,
    )

    db = FakeDB(
        user=user,
        role=role,
        permission=permission,
    )

    monkeypatch.setattr(
        rbac,
        "decode_access_token",
        lambda token: {"sub": "1"},
    )

    dependency = rbac.require_permission("OWN_ATTENDANCE")

    result = dependency(
        credentials=make_credentials(),
        db=db,
    )

    assert result is user
    assert result.id == 1


def test_permission_denied_returns_403(monkeypatch):
    user = SimpleNamespace(
        id=1,
        role_id=10,
        is_active=True,
    )

    role = SimpleNamespace(
        id=10,
        name="STUDENT",
    )

    permission = SimpleNamespace(
        role_id=10,
        intent="MARK_ATTENDANCE",
        allowed=False,
    )

    db = FakeDB(
        user=user,
        role=role,
        permission=permission,
    )

    monkeypatch.setattr(
        rbac,
        "decode_access_token",
        lambda token: {"sub": "1"},
    )

    dependency = rbac.require_permission("MARK_ATTENDANCE")

    with pytest.raises(HTTPException) as exc_info:
        dependency(
            credentials=make_credentials(),
            db=db,
        )

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == (
        "Permission denied for intent: MARK_ATTENDANCE"
    )


def test_inactive_user_returns_401(monkeypatch):
    user = SimpleNamespace(
        id=1,
        role_id=10,
        is_active=False,
    )

    db = FakeDB(user=user)

    monkeypatch.setattr(
        rbac,
        "decode_access_token",
        lambda token: {"sub": "1"},
    )

    dependency = rbac.require_permission("OWN_ATTENDANCE")

    with pytest.raises(HTTPException) as exc_info:
        dependency(
            credentials=make_credentials(),
            db=db,
        )

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "User not found or inactive"


def test_invalid_token_returns_401(monkeypatch):
    def raise_invalid_token(token):
        raise ValueError("invalid token")

    monkeypatch.setattr(
        rbac,
        "decode_access_token",
        raise_invalid_token,
    )

    db = FakeDB()

    dependency = rbac.require_permission("OWN_ATTENDANCE")

    with pytest.raises(HTTPException) as exc_info:
        dependency(
            credentials=make_credentials("bad-token"),
            db=db,
        )

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid or expired token"
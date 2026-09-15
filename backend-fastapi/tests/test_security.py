import pytest
from fastapi import HTTPException

from app.security import Role, authenticate, create_access_token, get_current_user, require_permission


def test_authenticate_accepts_correct_password():
    role = authenticate("driver-17", "changeme")
    assert role == Role.driver


def test_authenticate_rejects_wrong_password():
    with pytest.raises(HTTPException) as exc_info:
        authenticate("driver-17", "wrong-password")
    assert exc_info.value.status_code == 401


def test_authenticate_rejects_unknown_user():
    with pytest.raises(HTTPException) as exc_info:
        authenticate("nobody", "changeme")
    assert exc_info.value.status_code == 401


def test_token_round_trips_to_current_user():
    token = create_access_token("operator-1", Role.operator)
    user = get_current_user(authorization=f"Bearer {token}")
    assert user.operator_id == "operator-1"
    assert user.role == Role.operator


def test_get_current_user_rejects_malformed_header():
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(authorization="not-a-bearer-token")
    assert exc_info.value.status_code == 401


def test_get_current_user_rejects_bad_token():
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(authorization="Bearer garbage")
    assert exc_info.value.status_code == 401


def test_driver_cannot_release_brake():
    with pytest.raises(HTTPException) as exc_info:
        require_permission(Role.driver, "release_brake")
    assert exc_info.value.status_code == 403


def test_operator_can_release_brake():
    require_permission(Role.operator, "release_brake")

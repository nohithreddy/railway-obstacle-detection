import os
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Optional

from fastapi import Header, HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext

SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "dev-only-change-me")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Role(str, Enum):
    driver = "driver"
    operator = "operator"
    admin = "admin"


ROLE_PERMISSIONS = {
    Role.driver: {"read_alerts", "submit_driver_response"},
    Role.operator: {"read_alerts", "submit_driver_response", "release_brake", "activate_response"},
    Role.admin: {"read_alerts", "submit_driver_response", "release_brake", "activate_response", "manage_users"},
}

# Demo credential store. Replace with a real user table (and drop the default
# passwords) before this touches anything beyond a bench/demo network.
_DEMO_USERS = {
    "driver-17": {"password_hash": pwd_context.hash("changeme"), "role": Role.driver},
    "operator-1": {"password_hash": pwd_context.hash("changeme"), "role": Role.operator},
}


class CurrentUser:
    def __init__(self, operator_id: str, role: Role) -> None:
        self.operator_id = operator_id
        self.role = role


def authenticate(operator_id: str, password: str) -> Role:
    user = _DEMO_USERS.get(operator_id)
    if not user or not pwd_context.verify(password, user["password_hash"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return user["role"]


def create_access_token(operator_id: str, role: Role) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode({"sub": operator_id, "role": role.value, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(authorization: Optional[str] = Header(None)) -> CurrentUser:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")

    token = authorization.removeprefix("Bearer ")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    return CurrentUser(operator_id=payload["sub"], role=Role(payload["role"]))


def require_permission(role: Role, permission: str) -> None:
    if permission not in ROLE_PERMISSIONS[role]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Role {role.value} cannot perform {permission}",
        )

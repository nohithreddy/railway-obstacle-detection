from enum import Enum

from fastapi import HTTPException, status


class Role(str, Enum):
    driver = "driver"
    operator = "operator"
    admin = "admin"


ROLE_PERMISSIONS = {
    Role.driver: {"read_alerts", "submit_driver_response"},
    Role.operator: {"read_alerts", "submit_driver_response", "release_brake", "activate_response"},
    Role.admin: {"read_alerts", "submit_driver_response", "release_brake", "activate_response", "manage_users"},
}


def require_permission(role: Role, permission: str) -> None:
    if permission not in ROLE_PERMISSIONS[role]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Role {role.value} cannot perform {permission}",
        )

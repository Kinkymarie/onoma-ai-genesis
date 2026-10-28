"""Role based access control."""
from ..utils.constants import ROLE_ADMIN, ROLE_MEMBER, ROLE_VIEWER
from ..utils.exceptions import Forbidden

READ, WRITE, DELETE, ADMIN = "read", "write", "delete", "admin"

ROLE_PERMISSIONS: dict[str, frozenset[str]] = {
    ROLE_ADMIN: frozenset({READ, WRITE, DELETE, ADMIN}),
    ROLE_MEMBER: frozenset({READ, WRITE, DELETE}),
    ROLE_VIEWER: frozenset({READ}),
}


def has_permission(role: str, permission: str) -> bool:
    return permission in ROLE_PERMISSIONS.get(role, frozenset())


def require(role: str, permission: str) -> None:
    if not has_permission(role, permission):
        raise Forbidden(f"Missing permission: {permission}")

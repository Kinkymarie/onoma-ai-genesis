"""User management API."""
from fastapi import APIRouter, Depends

from ..dependencies import Container, get_container, get_current_user, require_permission
from ..models.schemas import Notification, User, UserOut, UserUpdate
from ..utils.exceptions import Forbidden
from ..utils.validators import validate_choice
from ..utils.constants import ROLES

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=list[UserOut])
def list_users(_: User = Depends(require_permission("admin")), c: Container = Depends(get_container)):
    return c.users.list()


@router.get("/me/notifications", response_model=list[Notification])
def my_notifications(unread: bool = False, user: User = Depends(get_current_user),
                     c: Container = Depends(get_container)):
    return c.notifications.list_for_user(user.id, unread)


@router.post("/me/notifications/{notification_id}/read", response_model=Notification)
def read_notification(notification_id: str, user: User = Depends(get_current_user),
                      c: Container = Depends(get_container)):
    return c.notifications.mark_read(user.id, notification_id)


@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: str, user: User = Depends(get_current_user), c: Container = Depends(get_container)):
    if user.id != user_id and user.role != "admin":
        raise Forbidden("Cannot view other users")
    return c.users.get(user_id)


@router.patch("/{user_id}", response_model=UserOut)
def update_user(user_id: str, data: UserUpdate, user: User = Depends(get_current_user),
                c: Container = Depends(get_container)):
    if user.id != user_id and user.role != "admin":
        raise Forbidden("Cannot modify other users")
    return c.users.update(user_id, data)


@router.put("/{user_id}/role", response_model=UserOut)
def set_role(user_id: str, role: str, admin: User = Depends(require_permission("admin")),
             c: Container = Depends(get_container)):
    validate_choice(role, ROLES, "role")
    result = c.users.set_role(user_id, role)
    c.audit.record(admin.id, "user.role_change", f"user:{user_id}", role=role)
    return result


@router.delete("/{user_id}", status_code=204)
def delete_user(user_id: str, user: User = Depends(get_current_user), c: Container = Depends(get_container)):
    if user.id != user_id and user.role != "admin":
        raise Forbidden("Cannot delete other users")
    c.users.delete(user_id)
    c.audit.record(user.id, "user.delete", f"user:{user_id}")

"""Auth decorators/dependencies for routes."""
from ..dependencies import get_current_user, require_permission

current_user = get_current_user
require_admin = require_permission("admin")
require_write = require_permission("write")

__all__ = ["current_user", "require_admin", "require_write", "require_permission"]

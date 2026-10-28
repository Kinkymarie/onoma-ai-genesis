"""Audit log API (admin only)."""
from fastapi import APIRouter, Depends

from ..dependencies import Container, get_container, require_permission
from ..models.schemas import AuditLog, User

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("", response_model=list[AuditLog])
def list_logs(user_id: str | None = None, limit: int = 100, _: User = Depends(require_permission("admin")),
              c: Container = Depends(get_container)):
    return c.audit.list(user_id, max(1, min(limit, 500)))

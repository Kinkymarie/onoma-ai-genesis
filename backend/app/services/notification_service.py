"""Notifications and audit logging."""
from __future__ import annotations

from ..db.repositories import Repositories
from ..models.schemas import AuditLog, Notification
from ..utils.exceptions import NotFound


class NotificationService:
    def __init__(self, repos: Repositories):
        self.repos = repos

    def notify(self, user_id: str, title: str, body: str = "") -> Notification:
        return self.repos.notifications.create(Notification(user_id=user_id, title=title, body=body))

    def list_for_user(self, user_id: str, unread_only: bool = False) -> list[Notification]:
        items = self.repos.notifications.for_user(user_id)
        return [n for n in items if not n.read] if unread_only else items

    def mark_read(self, user_id: str, notification_id: str) -> Notification:
        n = self.repos.notifications.get(notification_id)
        if n is None or n.user_id != user_id:
            raise NotFound("Notification not found")
        return self.repos.notifications.update(notification_id, read=True)


class AuditService:
    def __init__(self, repos: Repositories):
        self.repos = repos

    def record(self, user_id: str | None, action: str, resource: str = "", **detail) -> AuditLog:
        return self.repos.audit.create(AuditLog(user_id=user_id, action=action, resource=resource, detail=detail))

    def list(self, user_id: str | None = None, limit: int = 100) -> list[AuditLog]:
        logs = self.repos.audit.list((lambda a: a.user_id == user_id) if user_id else None)
        return logs[-limit:][::-1]

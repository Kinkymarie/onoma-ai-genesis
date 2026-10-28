"""Notification jobs."""
from datetime import datetime, timezone

from ..db.repositories import Repositories
from ..services.notification_service import NotificationService


def notify_overdue_tasks(repos: Repositories) -> int:
    """Notify assignees of overdue, unfinished tasks (once per task per day)."""
    service = NotificationService(repos)
    now = datetime.now(timezone.utc)
    sent = 0
    for task in repos.tasks.list(lambda t: t.status != "done" and t.assignee_id and t.due_date and t.due_date < now):
        title = f"Task overdue: {task.title}"
        existing = repos.notifications.for_user(task.assignee_id)
        if any(n.title == title and n.created_at.date() == now.date() for n in existing):
            continue
        service.notify(task.assignee_id, title)
        sent += 1
    return sent

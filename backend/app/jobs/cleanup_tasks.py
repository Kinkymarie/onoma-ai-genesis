"""Data cleanup jobs."""
from datetime import datetime, timedelta, timezone

from ..auth.jwt import blacklist
from ..db.repositories import Repositories


def purge_old_audit_logs(repos: Repositories, days: int = 90) -> int:
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    old = repos.audit.list(lambda a: a.created_at < cutoff)
    for a in old:
        repos.audit.delete(a.id)
    return len(old)


def purge_read_notifications(repos: Repositories, days: int = 30) -> int:
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    old = repos.notifications.list(lambda n: n.read and n.updated_at < cutoff)
    for n in old:
        repos.notifications.delete(n.id)
    return len(old)


def purge_expired_tokens() -> None:
    import time
    now = time.time()
    for jti in [k for k, v in blacklist._revoked.items() if v < now]:
        blacklist._revoked.pop(jti, None)

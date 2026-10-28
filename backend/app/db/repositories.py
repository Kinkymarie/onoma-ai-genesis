"""Repository layer. A generic in-memory base keeps the pattern backend-agnostic;
swap ``BaseRepository`` for a SQLAlchemy-backed implementation for PostgreSQL."""
from __future__ import annotations

import threading
from typing import Callable, Generic, TypeVar

from ..models.schemas import (
    Agent, Automation, BaseEntity, Conversation, Document, Entity, Memory, Notification,
    Organization, Project, Relationship, Task, User, Workspace, AuditLog, utcnow,
)

T = TypeVar("T", bound=BaseEntity)


class BaseRepository(Generic[T]):
    def __init__(self) -> None:
        self._items: dict[str, T] = {}
        self._lock = threading.RLock()

    def create(self, item: T) -> T:
        with self._lock:
            self._items[item.id] = item
        return item

    def get(self, item_id: str) -> T | None:
        return self._items.get(item_id)

    def update(self, item_id: str, **changes) -> T | None:
        with self._lock:
            item = self._items.get(item_id)
            if item is None:
                return None
            updated = item.model_copy(update={**changes, "updated_at": utcnow()})
            self._items[item_id] = updated
            return updated

    def delete(self, item_id: str) -> bool:
        with self._lock:
            return self._items.pop(item_id, None) is not None

    def list(self, predicate: Callable[[T], bool] | None = None) -> list[T]:
        with self._lock:
            items = list(self._items.values())
        items = [i for i in items if predicate(i)] if predicate else items
        return sorted(items, key=lambda i: i.created_at)

    def count(self) -> int:
        return len(self._items)

    def clear(self) -> None:
        with self._lock:
            self._items.clear()


class UserRepository(BaseRepository[User]):
    def get_by_email(self, email: str) -> User | None:
        email = email.lower()
        return next((u for u in self._items.values() if u.email.lower() == email), None)


class OrganizationRepository(BaseRepository[Organization]):
    def get_by_slug(self, slug: str) -> Organization | None:
        return next((o for o in self._items.values() if o.slug == slug), None)

    def for_user(self, user_id: str) -> list[Organization]:
        return self.list(lambda o: o.owner_id == user_id or user_id in o.member_ids)


class WorkspaceRepository(BaseRepository[Workspace]):
    def for_user(self, user_id: str) -> list[Workspace]:
        return self.list(lambda w: w.owner_id == user_id or user_id in w.member_ids)


class _WorkspaceScoped(BaseRepository[T]):
    def for_workspace(self, workspace_id: str) -> list[T]:
        return self.list(lambda i: i.workspace_id == workspace_id)


class ProjectRepository(_WorkspaceScoped[Project]):
    pass


class DocumentRepository(_WorkspaceScoped[Document]):
    pass


class TaskRepository(_WorkspaceScoped[Task]):
    pass


class AgentRepository(_WorkspaceScoped[Agent]):
    pass


class AutomationRepository(_WorkspaceScoped[Automation]):
    pass


class MemoryRepository(_WorkspaceScoped[Memory]):
    pass


class EntityRepository(_WorkspaceScoped[Entity]):
    pass


class RelationshipRepository(_WorkspaceScoped[Relationship]):
    pass


class ConversationRepository(BaseRepository[Conversation]):
    def for_user(self, user_id: str) -> list[Conversation]:
        return self.list(lambda c: c.user_id == user_id)


class NotificationRepository(BaseRepository[Notification]):
    def for_user(self, user_id: str) -> list[Notification]:
        return self.list(lambda n: n.user_id == user_id)


class AuditLogRepository(BaseRepository[AuditLog]):
    pass


class Repositories:
    """Container bundling every repository."""

    def __init__(self) -> None:
        self.users = UserRepository()
        self.organizations = OrganizationRepository()
        self.workspaces = WorkspaceRepository()
        self.projects = ProjectRepository()
        self.documents = DocumentRepository()
        self.tasks = TaskRepository()
        self.agents = AgentRepository()
        self.automations = AutomationRepository()
        self.memories = MemoryRepository()
        self.entities = EntityRepository()
        self.relationships = RelationshipRepository()
        self.conversations = ConversationRepository()
        self.notifications = NotificationRepository()
        self.audit = AuditLogRepository()

    def reset(self) -> None:
        for repo in vars(self).values():
            repo.clear()

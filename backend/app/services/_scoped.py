"""Shared helper for workspace-scoped CRUD services."""
from __future__ import annotations

from ..db.repositories import Repositories
from ..models.schemas import User
from ..utils.exceptions import NotFound
from .workspace_service import WorkspaceService


class ScopedService:
    repo_name: str
    label: str

    def __init__(self, repos: Repositories, workspaces: WorkspaceService):
        self.repos = repos
        self.workspaces = workspaces

    @property
    def repo(self):
        return getattr(self.repos, self.repo_name)

    def _create(self, user: User, model, data):
        self.workspaces.get(user, data.workspace_id, write=True)
        return self.repo.create(model(created_by=user.id, **data.model_dump()))

    def list(self, user: User, workspace_id: str):
        self.workspaces.get(user, workspace_id)
        return self.repo.for_workspace(workspace_id)

    def get(self, user: User, item_id: str, write: bool = False):
        item = self.repo.get(item_id)
        if item is None:
            raise NotFound(f"{self.label} not found")
        self.workspaces.get(user, item.workspace_id, write=write)
        return item

    def update(self, user: User, item_id: str, data):
        self.get(user, item_id, write=True)
        return self.repo.update(item_id, **data.model_dump(exclude_unset=True))

    def delete(self, user: User, item_id: str) -> None:
        self.get(user, item_id, write=True)
        self.repo.delete(item_id)

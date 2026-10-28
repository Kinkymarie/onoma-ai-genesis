"""Project management."""
from __future__ import annotations

from ..models.schemas import Project, ProjectCreate, User
from ._scoped import ScopedService


class ProjectService(ScopedService):
    repo_name, label = "projects", "Project"

    def create(self, user: User, data: ProjectCreate) -> Project:
        return self._create(user, Project, data)

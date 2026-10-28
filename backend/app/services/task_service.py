"""Task management."""
from __future__ import annotations

from ..models.schemas import Task, TaskCreate, User
from ..utils.exceptions import BadRequest, NotFound
from ._scoped import ScopedService


class TaskService(ScopedService):
    repo_name, label = "tasks", "Task"

    def create(self, user: User, data: TaskCreate) -> Task:
        ws = self.workspaces.get(user, data.workspace_id, write=True)
        if data.project_id:
            project = self.repos.projects.get(data.project_id)
            if project is None or project.workspace_id != data.workspace_id:
                raise NotFound("Project not found in workspace")
        if data.assignee_id and data.assignee_id != ws.owner_id and data.assignee_id not in ws.member_ids:
            raise BadRequest("Assignee must be a workspace member")
        return self._create(user, Task, data)

    def list(self, user: User, workspace_id: str, status: str | None = None, project_id: str | None = None):
        tasks = super().list(user, workspace_id)
        return [t for t in tasks
                if (status is None or t.status == status) and (project_id is None or t.project_id == project_id)]

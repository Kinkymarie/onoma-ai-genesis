"""Document operations."""
from __future__ import annotations

from ..models.schemas import Document, DocumentCreate, User
from ..utils.exceptions import NotFound
from ._scoped import ScopedService


class DocumentService(ScopedService):
    repo_name, label = "documents", "Document"

    def create(self, user: User, data: DocumentCreate) -> Document:
        if data.project_id:
            project = self.repos.projects.get(data.project_id)
            if project is None or project.workspace_id != data.workspace_id:
                raise NotFound("Project not found in workspace")
        return self._create(user, Document, data)

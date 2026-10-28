"""Service container and FastAPI dependencies."""
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .auth import jwt as jwt_tokens
from .auth.permissions import require
from .db.repositories import Repositories
from .models.schemas import User
from .services.agent_service import AgentService, AutomationService
from .services.chat_service import ChatService
from .services.document_service import DocumentService
from .services.memory_service import MemoryService
from .services.notification_service import AuditService, NotificationService
from .services.project_service import ProjectService
from .services.search_service import SearchService
from .services.task_service import TaskService
from .services.user_service import UserService
from .services.workspace_service import WorkspaceService
from .utils.exceptions import Unauthorized


class Container:
    def __init__(self) -> None:
        self.repos = Repositories()
        self.users = UserService(self.repos)
        self.workspaces = WorkspaceService(self.repos)
        self.projects = ProjectService(self.repos, self.workspaces)
        self.documents = DocumentService(self.repos, self.workspaces)
        self.tasks = TaskService(self.repos, self.workspaces)
        self.agents = AgentService(self.repos, self.workspaces)
        self.automations = AutomationService(self.repos, self.workspaces)
        self.memory = MemoryService(self.repos, self.workspaces)
        self.search = SearchService(self.repos, self.workspaces)
        self.chat = ChatService(self.repos, self.workspaces)
        self.notifications = NotificationService(self.repos)
        self.audit = AuditService(self.repos)


container = Container()


def get_container() -> Container:
    return container


_bearer = HTTPBearer(auto_error=False)


def get_current_user(creds: HTTPAuthorizationCredentials | None = Depends(_bearer)) -> User:
    if creds is None:
        raise Unauthorized("Not authenticated")
    payload = jwt_tokens.decode_token(creds.credentials)
    user = container.repos.users.get(payload["sub"])
    if user is None or not user.is_active:
        raise Unauthorized("User not found or inactive")
    return user


def require_permission(permission: str):
    def dep(user: User = Depends(get_current_user)) -> User:
        require(user.role, permission)
        return user
    return dep

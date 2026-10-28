"""Domain models and Pydantic schemas for all CRUD operations."""
from datetime import datetime, timezone
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from ..utils.validators import validate_password_strength

Role = Literal["admin", "member", "viewer"]
TaskStatus = Literal["todo", "in_progress", "done", "blocked"]
TaskPriority = Literal["low", "medium", "high", "urgent"]
ProjectStatus = Literal["active", "archived", "completed"]


def new_id() -> str:
    return uuid4().hex


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class BaseEntity(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(default_factory=new_id)
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)


# ---- Users ----
class User(BaseEntity):
    email: str
    name: str
    password_hash: str | None = None
    role: Role = "member"
    is_active: bool = True
    is_verified: bool = False
    totp_secret: str | None = None
    totp_enabled: bool = False
    oauth_provider: str | None = None


class UserCreate(BaseModel):
    email: EmailStr
    name: str = Field(min_length=1, max_length=100)
    password: str

    @field_validator("password")
    @classmethod
    def _strong(cls, v: str) -> str:
        return validate_password_strength(v)


class UserUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    email: EmailStr | None = None


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: str
    name: str
    role: Role
    is_active: bool
    is_verified: bool
    totp_enabled: bool
    created_at: datetime


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    totp_code: str | None = None


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class PasswordChange(BaseModel):
    current_password: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def _strong(cls, v: str) -> str:
        return validate_password_strength(v)


class TotpCode(BaseModel):
    code: str = Field(min_length=6, max_length=8)


# ---- Organizations / Workspaces ----
class Organization(BaseEntity):
    name: str
    slug: str
    owner_id: str
    member_ids: list[str] = Field(default_factory=list)


class OrganizationCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    slug: str | None = None


class OrganizationUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)


class Workspace(BaseEntity):
    name: str
    description: str = ""
    organization_id: str | None = None
    owner_id: str
    member_ids: list[str] = Field(default_factory=list)


class WorkspaceCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str = ""
    organization_id: str | None = None


class WorkspaceUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = None


class MemberAdd(BaseModel):
    user_id: str


# ---- Projects / Documents / Tasks ----
class Project(BaseEntity):
    workspace_id: str
    name: str
    description: str = ""
    status: ProjectStatus = "active"
    created_by: str


class ProjectCreate(BaseModel):
    workspace_id: str
    name: str = Field(min_length=1, max_length=200)
    description: str = ""


class ProjectUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    status: ProjectStatus | None = None


class Document(BaseEntity):
    workspace_id: str
    project_id: str | None = None
    title: str
    content: str = ""
    tags: list[str] = Field(default_factory=list)
    created_by: str


class DocumentCreate(BaseModel):
    workspace_id: str
    project_id: str | None = None
    title: str = Field(min_length=1, max_length=300)
    content: str = ""
    tags: list[str] = Field(default_factory=list)


class DocumentUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=300)
    content: str | None = None
    tags: list[str] | None = None


class Task(BaseEntity):
    workspace_id: str
    project_id: str | None = None
    title: str
    description: str = ""
    status: TaskStatus = "todo"
    priority: TaskPriority = "medium"
    assignee_id: str | None = None
    due_date: datetime | None = None
    created_by: str


class TaskCreate(BaseModel):
    workspace_id: str
    project_id: str | None = None
    title: str = Field(min_length=1, max_length=300)
    description: str = ""
    status: TaskStatus = "todo"
    priority: TaskPriority = "medium"
    assignee_id: str | None = None
    due_date: datetime | None = None


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=300)
    description: str | None = None
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    assignee_id: str | None = None
    due_date: datetime | None = None


# ---- Agents / Automations ----
class Agent(BaseEntity):
    workspace_id: str
    name: str
    description: str = ""
    system_prompt: str = "You are a helpful assistant."
    provider: str | None = None
    model: str | None = None
    tools: list[str] = Field(default_factory=list)
    created_by: str


class AgentCreate(BaseModel):
    workspace_id: str
    name: str = Field(min_length=1, max_length=100)
    description: str = ""
    system_prompt: str = "You are a helpful assistant."
    provider: str | None = None
    model: str | None = None
    tools: list[str] = Field(default_factory=list)


class AgentUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = None
    system_prompt: str | None = None
    provider: str | None = None
    model: str | None = None
    tools: list[str] | None = None


class AgentRunRequest(BaseModel):
    input: str = Field(min_length=1)
    max_steps: int = Field(default=5, ge=1, le=10)


class Automation(BaseEntity):
    workspace_id: str
    name: str
    trigger: str
    action: dict[str, Any] = Field(default_factory=dict)
    enabled: bool = True
    created_by: str


class AutomationCreate(BaseModel):
    workspace_id: str
    name: str = Field(min_length=1, max_length=100)
    trigger: str = Field(min_length=1)
    action: dict[str, Any] = Field(default_factory=dict)
    enabled: bool = True


class AutomationUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    trigger: str | None = None
    action: dict[str, Any] | None = None
    enabled: bool | None = None


# ---- Memory / Knowledge graph ----
class Memory(BaseEntity):
    workspace_id: str
    user_id: str
    content: str
    kind: str = "note"
    embedding: list[float] = Field(default_factory=list)


class MemoryCreate(BaseModel):
    workspace_id: str
    content: str = Field(min_length=1)
    kind: str = "note"


class Entity(BaseEntity):
    """Knowledge-graph entity."""

    workspace_id: str
    name: str
    type: str = "concept"
    properties: dict[str, Any] = Field(default_factory=dict)



class EntityCreate(BaseModel):
    workspace_id: str
    name: str = Field(min_length=1)
    type: str = "concept"
    properties: dict[str, Any] = Field(default_factory=dict)


class Relationship(BaseEntity):
    workspace_id: str
    source_id: str
    target_id: str
    type: str = "related_to"


class RelationshipCreate(BaseModel):
    workspace_id: str
    source_id: str
    target_id: str
    type: str = "related_to"


# ---- Conversations / notifications / audit ----
class Message(BaseModel):
    role: Literal["system", "user", "assistant", "tool"]
    content: str
    created_at: datetime = Field(default_factory=utcnow)


class Conversation(BaseEntity):
    user_id: str
    workspace_id: str | None = None
    title: str = "New conversation"
    messages: list[Message] = Field(default_factory=list)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=20000)
    conversation_id: str | None = None
    workspace_id: str | None = None
    provider: str | None = None
    use_rag: bool = False


class Notification(BaseEntity):
    user_id: str
    title: str
    body: str = ""
    read: bool = False


class AuditLog(BaseEntity):
    user_id: str | None
    action: str
    resource: str = ""
    detail: dict[str, Any] = Field(default_factory=dict)


class SearchResult(BaseModel):
    type: str
    id: str
    title: str
    snippet: str = ""
    score: float = 0.0


class EmbeddingRequest(BaseModel):
    texts: list[str] = Field(min_length=1, max_length=100)

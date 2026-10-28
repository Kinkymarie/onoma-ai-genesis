"""Workspace and organization operations plus access control."""
from __future__ import annotations

from ..auth.permissions import require
from ..db.repositories import Repositories
from ..models.schemas import (
    Organization, OrganizationCreate, OrganizationUpdate, User, Workspace, WorkspaceCreate, WorkspaceUpdate,
)
from ..utils.exceptions import Conflict, Forbidden, NotFound
from ..utils.validators import slugify


class WorkspaceService:
    def __init__(self, repos: Repositories):
        self.repos = repos

    # ---- workspaces ----
    def create(self, user: User, data: WorkspaceCreate) -> Workspace:
        require(user.role, "write")
        if data.organization_id:
            self.get_org(user, data.organization_id)
        return self.repos.workspaces.create(Workspace(owner_id=user.id, **data.model_dump()))

    def list(self, user: User) -> list[Workspace]:
        if user.role == "admin":
            return self.repos.workspaces.list()
        return self.repos.workspaces.for_user(user.id)

    def get(self, user: User, workspace_id: str, write: bool = False) -> Workspace:
        """Fetch a workspace, enforcing membership (and write permission)."""
        ws = self.repos.workspaces.get(workspace_id)
        if ws is None:
            raise NotFound("Workspace not found")
        if user.role != "admin" and user.id != ws.owner_id and user.id not in ws.member_ids:
            raise Forbidden("No access to this workspace")
        if write:
            require(user.role, "write")
        return ws

    def update(self, user: User, workspace_id: str, data: WorkspaceUpdate) -> Workspace:
        self.get(user, workspace_id, write=True)
        return self.repos.workspaces.update(workspace_id, **data.model_dump(exclude_unset=True, exclude_none=True))

    def delete(self, user: User, workspace_id: str) -> None:
        ws = self.get(user, workspace_id, write=True)
        if user.role != "admin" and ws.owner_id != user.id:
            raise Forbidden("Only the owner can delete a workspace")
        self.repos.workspaces.delete(workspace_id)

    def add_member(self, user: User, workspace_id: str, member_id: str) -> Workspace:
        ws = self.get(user, workspace_id, write=True)
        if user.role != "admin" and ws.owner_id != user.id:
            raise Forbidden("Only the owner can manage members")
        if self.repos.users.get(member_id) is None:
            raise NotFound("User not found")
        if member_id in ws.member_ids or member_id == ws.owner_id:
            return ws
        return self.repos.workspaces.update(workspace_id, member_ids=[*ws.member_ids, member_id])

    def remove_member(self, user: User, workspace_id: str, member_id: str) -> Workspace:
        ws = self.get(user, workspace_id, write=True)
        if user.role != "admin" and ws.owner_id != user.id:
            raise Forbidden("Only the owner can manage members")
        return self.repos.workspaces.update(workspace_id, member_ids=[m for m in ws.member_ids if m != member_id])

    # ---- organizations ----
    def create_org(self, user: User, data: OrganizationCreate) -> Organization:
        require(user.role, "write")
        slug = slugify(data.slug or data.name)
        if self.repos.organizations.get_by_slug(slug):
            raise Conflict("Organization slug already in use")
        return self.repos.organizations.create(Organization(name=data.name, slug=slug, owner_id=user.id))

    def list_orgs(self, user: User) -> list[Organization]:
        if user.role == "admin":
            return self.repos.organizations.list()
        return self.repos.organizations.for_user(user.id)

    def get_org(self, user: User, org_id: str) -> Organization:
        org = self.repos.organizations.get(org_id)
        if org is None:
            raise NotFound("Organization not found")
        if user.role != "admin" and user.id != org.owner_id and user.id not in org.member_ids:
            raise Forbidden("No access to this organization")
        return org

    def update_org(self, user: User, org_id: str, data: OrganizationUpdate) -> Organization:
        org = self.get_org(user, org_id)
        require(user.role, "write")
        if user.role != "admin" and org.owner_id != user.id:
            raise Forbidden("Only the owner can update an organization")
        return self.repos.organizations.update(org_id, **data.model_dump(exclude_unset=True, exclude_none=True))

    def delete_org(self, user: User, org_id: str) -> None:
        org = self.get_org(user, org_id)
        if user.role != "admin" and org.owner_id != user.id:
            raise Forbidden("Only the owner can delete an organization")
        self.repos.organizations.delete(org_id)

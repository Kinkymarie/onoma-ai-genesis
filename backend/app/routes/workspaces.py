"""Workspace API."""
from fastapi import APIRouter, Depends

from ..dependencies import Container, get_container, get_current_user
from ..models.schemas import MemberAdd, User, Workspace, WorkspaceCreate, WorkspaceUpdate

router = APIRouter(prefix="/workspaces", tags=["workspaces"])


@router.post("", response_model=Workspace, status_code=201)
def create(data: WorkspaceCreate, user: User = Depends(get_current_user), c: Container = Depends(get_container)):
    ws = c.workspaces.create(user, data)
    c.audit.record(user.id, "workspace.create", f"workspace:{ws.id}")
    return ws


@router.get("", response_model=list[Workspace])
def list_workspaces(user: User = Depends(get_current_user), c: Container = Depends(get_container)):
    return c.workspaces.list(user)


@router.get("/{workspace_id}", response_model=Workspace)
def get(workspace_id: str, user: User = Depends(get_current_user), c: Container = Depends(get_container)):
    return c.workspaces.get(user, workspace_id)


@router.patch("/{workspace_id}", response_model=Workspace)
def update(workspace_id: str, data: WorkspaceUpdate, user: User = Depends(get_current_user),
           c: Container = Depends(get_container)):
    return c.workspaces.update(user, workspace_id, data)


@router.delete("/{workspace_id}", status_code=204)
def delete(workspace_id: str, user: User = Depends(get_current_user), c: Container = Depends(get_container)):
    c.workspaces.delete(user, workspace_id)
    c.audit.record(user.id, "workspace.delete", f"workspace:{workspace_id}")


@router.post("/{workspace_id}/members", response_model=Workspace)
def add_member(workspace_id: str, data: MemberAdd, user: User = Depends(get_current_user),
               c: Container = Depends(get_container)):
    ws = c.workspaces.add_member(user, workspace_id, data.user_id)
    c.notifications.notify(data.user_id, "Added to workspace", ws.name)
    return ws


@router.delete("/{workspace_id}/members/{member_id}", response_model=Workspace)
def remove_member(workspace_id: str, member_id: str, user: User = Depends(get_current_user),
                  c: Container = Depends(get_container)):
    return c.workspaces.remove_member(user, workspace_id, member_id)

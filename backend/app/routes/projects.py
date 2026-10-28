"""Project API."""
from fastapi import APIRouter, Depends

from ..dependencies import Container, get_container, get_current_user
from ..models.schemas import Project, ProjectCreate, ProjectUpdate, User

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("", response_model=Project, status_code=201)
def create(data: ProjectCreate, user: User = Depends(get_current_user), c: Container = Depends(get_container)):
    item = c.projects.create(user, data)
    c.audit.record(user.id, "project.create", f"project:{item.id}")
    return item


@router.get("", response_model=list[Project])
def list_items(workspace_id: str, user: User = Depends(get_current_user),
               c: Container = Depends(get_container)):
    return c.projects.list(user, workspace_id)


@router.get("/{item_id}", response_model=Project)
def get(item_id: str, user: User = Depends(get_current_user), c: Container = Depends(get_container)):
    return c.projects.get(user, item_id)


@router.patch("/{item_id}", response_model=Project)
def update(item_id: str, data: ProjectUpdate, user: User = Depends(get_current_user),
           c: Container = Depends(get_container)):
    return c.projects.update(user, item_id, data)


@router.delete("/{item_id}", status_code=204)
def delete(item_id: str, user: User = Depends(get_current_user), c: Container = Depends(get_container)):
    c.projects.delete(user, item_id)
    c.audit.record(user.id, "project.delete", f"project:{item_id}")

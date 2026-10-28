"""Task API."""
from fastapi import APIRouter, Depends

from ..dependencies import Container, get_container, get_current_user
from ..models.schemas import Task, TaskCreate, TaskUpdate, User

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("", response_model=Task, status_code=201)
def create(data: TaskCreate, user: User = Depends(get_current_user), c: Container = Depends(get_container)):
    item = c.tasks.create(user, data)
    c.audit.record(user.id, "task.create", f"task:{item.id}")
    return item


@router.get("", response_model=list[Task])
def list_items(workspace_id: str, status: str | None = None, project_id: str | None = None, user: User = Depends(get_current_user),
               c: Container = Depends(get_container)):
    return c.tasks.list(user, workspace_id, status, project_id)


@router.get("/{item_id}", response_model=Task)
def get(item_id: str, user: User = Depends(get_current_user), c: Container = Depends(get_container)):
    return c.tasks.get(user, item_id)


@router.patch("/{item_id}", response_model=Task)
def update(item_id: str, data: TaskUpdate, user: User = Depends(get_current_user),
           c: Container = Depends(get_container)):
    return c.tasks.update(user, item_id, data)


@router.delete("/{item_id}", status_code=204)
def delete(item_id: str, user: User = Depends(get_current_user), c: Container = Depends(get_container)):
    c.tasks.delete(user, item_id)
    c.audit.record(user.id, "task.delete", f"task:{item_id}")

"""Automation API."""
from fastapi import APIRouter, Depends

from ..dependencies import Container, get_container, get_current_user
from ..models.schemas import Automation, AutomationCreate, AutomationUpdate, User

router = APIRouter(prefix="/automations", tags=["automations"])


@router.post("", response_model=Automation, status_code=201)
def create(data: AutomationCreate, user: User = Depends(get_current_user), c: Container = Depends(get_container)):
    item = c.automations.create(user, data)
    c.audit.record(user.id, "automation.create", f"automation:{item.id}")
    return item


@router.get("", response_model=list[Automation])
def list_items(workspace_id: str, user: User = Depends(get_current_user),
               c: Container = Depends(get_container)):
    return c.automations.list(user, workspace_id)


@router.get("/{item_id}", response_model=Automation)
def get(item_id: str, user: User = Depends(get_current_user), c: Container = Depends(get_container)):
    return c.automations.get(user, item_id)


@router.patch("/{item_id}", response_model=Automation)
def update(item_id: str, data: AutomationUpdate, user: User = Depends(get_current_user),
           c: Container = Depends(get_container)):
    return c.automations.update(user, item_id, data)


@router.delete("/{item_id}", status_code=204)
def delete(item_id: str, user: User = Depends(get_current_user), c: Container = Depends(get_container)):
    c.automations.delete(user, item_id)
    c.audit.record(user.id, "automation.delete", f"automation:{item_id}")

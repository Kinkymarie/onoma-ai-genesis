"""Organization API."""
from fastapi import APIRouter, Depends

from ..dependencies import Container, get_container, get_current_user
from ..models.schemas import Organization, OrganizationCreate, OrganizationUpdate, User

router = APIRouter(prefix="/organizations", tags=["organizations"])


@router.post("", response_model=Organization, status_code=201)
def create(data: OrganizationCreate, user: User = Depends(get_current_user), c: Container = Depends(get_container)):
    return c.workspaces.create_org(user, data)


@router.get("", response_model=list[Organization])
def list_orgs(user: User = Depends(get_current_user), c: Container = Depends(get_container)):
    return c.workspaces.list_orgs(user)


@router.get("/{org_id}", response_model=Organization)
def get(org_id: str, user: User = Depends(get_current_user), c: Container = Depends(get_container)):
    return c.workspaces.get_org(user, org_id)


@router.patch("/{org_id}", response_model=Organization)
def update(org_id: str, data: OrganizationUpdate, user: User = Depends(get_current_user),
           c: Container = Depends(get_container)):
    return c.workspaces.update_org(user, org_id, data)


@router.delete("/{org_id}", status_code=204)
def delete(org_id: str, user: User = Depends(get_current_user), c: Container = Depends(get_container)):
    c.workspaces.delete_org(user, org_id)

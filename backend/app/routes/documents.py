"""Document API."""
from fastapi import APIRouter, Depends

from ..dependencies import Container, get_container, get_current_user
from ..models.schemas import Document, DocumentCreate, DocumentUpdate, User

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("", response_model=Document, status_code=201)
def create(data: DocumentCreate, user: User = Depends(get_current_user), c: Container = Depends(get_container)):
    item = c.documents.create(user, data)
    c.audit.record(user.id, "document.create", f"document:{item.id}")
    return item


@router.get("", response_model=list[Document])
def list_items(workspace_id: str, user: User = Depends(get_current_user),
               c: Container = Depends(get_container)):
    return c.documents.list(user, workspace_id)


@router.get("/{item_id}", response_model=Document)
def get(item_id: str, user: User = Depends(get_current_user), c: Container = Depends(get_container)):
    return c.documents.get(user, item_id)


@router.patch("/{item_id}", response_model=Document)
def update(item_id: str, data: DocumentUpdate, user: User = Depends(get_current_user),
           c: Container = Depends(get_container)):
    return c.documents.update(user, item_id, data)


@router.delete("/{item_id}", status_code=204)
def delete(item_id: str, user: User = Depends(get_current_user), c: Container = Depends(get_container)):
    c.documents.delete(user, item_id)
    c.audit.record(user.id, "document.delete", f"document:{item_id}")

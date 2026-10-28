"""Memory and knowledge-graph API."""
from fastapi import APIRouter, Depends

from ..dependencies import Container, get_container, get_current_user
from ..models.schemas import (
    Entity, EntityCreate, Memory, MemoryCreate, Relationship, RelationshipCreate, User,
)

router = APIRouter(prefix="/memory", tags=["memory"])
_EXCLUDE = {"embedding"}


@router.post("", response_model=Memory, response_model_exclude=_EXCLUDE, status_code=201)
async def remember(data: MemoryCreate, user: User = Depends(get_current_user), c: Container = Depends(get_container)):
    return await c.memory.remember(user, data)


@router.get("", response_model=list[Memory], response_model_exclude=_EXCLUDE)
def list_memories(workspace_id: str, user: User = Depends(get_current_user), c: Container = Depends(get_container)):
    return c.memory.list(user, workspace_id)


@router.get("/recall")
async def recall(workspace_id: str, query: str, k: int = 5, user: User = Depends(get_current_user),
                 c: Container = Depends(get_container)):
    results = await c.memory.recall(user, workspace_id, query, max(1, min(k, 50)))
    return [{"memory": m.model_dump(exclude=_EXCLUDE), "score": s} for m, s in results]


@router.delete("/{memory_id}", status_code=204)
def forget(memory_id: str, user: User = Depends(get_current_user), c: Container = Depends(get_container)):
    c.memory.forget(user, memory_id)


@router.post("/entities", response_model=Entity, status_code=201)
def add_entity(data: EntityCreate, user: User = Depends(get_current_user), c: Container = Depends(get_container)):
    return c.memory.add_entity(user, data)


@router.post("/relationships", response_model=Relationship, status_code=201)
def add_relationship(data: RelationshipCreate, user: User = Depends(get_current_user),
                     c: Container = Depends(get_container)):
    return c.memory.add_relationship(user, data)


@router.get("/graph")
def graph(workspace_id: str, user: User = Depends(get_current_user), c: Container = Depends(get_container)):
    return c.memory.graph(user, workspace_id)

"""Search API."""
from fastapi import APIRouter, Depends

from ..dependencies import Container, get_container, get_current_user
from ..models.schemas import SearchResult, User

router = APIRouter(prefix="/search", tags=["search"])


@router.get("", response_model=list[SearchResult])
def keyword(workspace_id: str, q: str, limit: int = 20, user: User = Depends(get_current_user),
            c: Container = Depends(get_container)):
    return c.search.keyword(user, workspace_id, q, max(1, min(limit, 100)))


@router.get("/semantic", response_model=list[SearchResult])
async def semantic(workspace_id: str, q: str, limit: int = 10, user: User = Depends(get_current_user),
                   c: Container = Depends(get_container)):
    return await c.search.semantic(user, workspace_id, q, max(1, min(limit, 100)))

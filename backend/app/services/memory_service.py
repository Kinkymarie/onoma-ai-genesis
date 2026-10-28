"""Memory storage and the knowledge graph."""
from __future__ import annotations

from ..ai.embeddings import cosine_similarity, embed_texts
from ..db.repositories import Repositories
from ..models.schemas import (
    Entity, EntityCreate, Memory, MemoryCreate, Relationship, RelationshipCreate, User,
)
from ..utils.exceptions import NotFound
from .workspace_service import WorkspaceService


class MemoryService:
    def __init__(self, repos: Repositories, workspaces: WorkspaceService):
        self.repos = repos
        self.workspaces = workspaces

    async def remember(self, user: User, data: MemoryCreate) -> Memory:
        self.workspaces.get(user, data.workspace_id, write=True)
        vec = (await embed_texts([data.content]))[0]
        return self.repos.memories.create(Memory(user_id=user.id, embedding=vec, **data.model_dump()))

    def list(self, user: User, workspace_id: str) -> list[Memory]:
        self.workspaces.get(user, workspace_id)
        return self.repos.memories.for_workspace(workspace_id)

    async def recall(self, user: User, workspace_id: str, query: str, k: int = 5) -> list[tuple[Memory, float]]:
        memories = self.list(user, workspace_id)
        if not memories:
            return []
        qvec = (await embed_texts([query]))[0]
        scored = [(m, cosine_similarity(qvec, m.embedding)) for m in memories]
        return sorted((s for s in scored if s[1] > 0), key=lambda s: s[1], reverse=True)[:k]

    def forget(self, user: User, memory_id: str) -> None:
        mem = self.repos.memories.get(memory_id)
        if mem is None:
            raise NotFound("Memory not found")
        self.workspaces.get(user, mem.workspace_id, write=True)
        self.repos.memories.delete(memory_id)

    # ---- knowledge graph ----
    def add_entity(self, user: User, data: EntityCreate) -> Entity:
        self.workspaces.get(user, data.workspace_id, write=True)
        return self.repos.entities.create(Entity(**data.model_dump()))

    def add_relationship(self, user: User, data: RelationshipCreate) -> Relationship:
        self.workspaces.get(user, data.workspace_id, write=True)
        for eid in (data.source_id, data.target_id):
            ent = self.repos.entities.get(eid)
            if ent is None or ent.workspace_id != data.workspace_id:
                raise NotFound("Entity not found in workspace")
        return self.repos.relationships.create(Relationship(**data.model_dump()))

    def graph(self, user: User, workspace_id: str) -> dict:
        self.workspaces.get(user, workspace_id)
        return {"entities": self.repos.entities.for_workspace(workspace_id),
                "relationships": self.repos.relationships.for_workspace(workspace_id)}

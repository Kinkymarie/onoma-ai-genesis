"""Keyword + semantic search across workspace content."""
from __future__ import annotations

import re

from ..ai.embeddings import cosine_similarity, embed_texts
from ..db.repositories import Repositories
from ..models.schemas import SearchResult, User
from .workspace_service import WorkspaceService


def _snippet(text: str, term: str, width: int = 80) -> str:
    idx = text.lower().find(term.lower())
    start = max(idx - width // 2, 0) if idx >= 0 else 0
    return text[start:start + width]


class SearchService:
    def __init__(self, repos: Repositories, workspaces: WorkspaceService):
        self.repos = repos
        self.workspaces = workspaces

    def keyword(self, user: User, workspace_id: str, query: str, limit: int = 20) -> list[SearchResult]:
        self.workspaces.get(user, workspace_id)
        terms = [t for t in re.findall(r"\w+", query.lower()) if t]
        if not terms:
            return []
        results: list[SearchResult] = []
        candidates = (
            [("document", d.id, d.title, d.content) for d in self.repos.documents.for_workspace(workspace_id)]
            + [("project", p.id, p.name, p.description) for p in self.repos.projects.for_workspace(workspace_id)]
            + [("task", t.id, t.title, t.description) for t in self.repos.tasks.for_workspace(workspace_id)]
        )
        for kind, rid, title, body in candidates:
            hay_title, hay_body = title.lower(), body.lower()
            score = sum(2.0 * (t in hay_title) + 1.0 * (t in hay_body) for t in terms) / (2 * len(terms))
            if score > 0:
                results.append(SearchResult(type=kind, id=rid, title=title, score=score,
                                            snippet=_snippet(body or title, terms[0])))
        return sorted(results, key=lambda r: r.score, reverse=True)[:limit]

    async def semantic(self, user: User, workspace_id: str, query: str, limit: int = 10) -> list[SearchResult]:
        self.workspaces.get(user, workspace_id)
        docs = self.repos.documents.for_workspace(workspace_id)
        if not docs:
            return []
        vectors = await embed_texts([query] + [f"{d.title}\n{d.content}" for d in docs])
        scored = [(d, cosine_similarity(vectors[0], v)) for d, v in zip(docs, vectors[1:])]
        return [SearchResult(type="document", id=d.id, title=d.title, score=s, snippet=d.content[:80])
                for d, s in sorted(scored, key=lambda x: x[1], reverse=True)[:limit] if s > 0]

from __future__ import annotations

from sqlalchemy.orm import Session

from ..models import AgentLog
from . import rag
from .providers import get_provider

AGENTS = {
    "research": ("Research Agent", "You are a research agent. Synthesize evidence and cite sources as [n]."),
    "code": ("Developer Agent", "You are a senior software engineer. Provide correct, tested code."),
    "architect": ("Systems Architect", "You are a systems architect. Design scalable, secure architectures."),
    "security": ("Security Agent", "You are a defensive security reviewer for authorized assessments only."),
    "executive": ("Executive Orchestrator", "You plan and coordinate complex work step by step."),
}


def list_agents() -> list[dict]:
    return [{"id": k, "name": v[0], "status": "ready"} for k, v in AGENTS.items()]


def execute(db: Session, user_id: int, agent_id: str, text: str, provider: str | None = None,
            use_rag: bool = True) -> dict:
    if agent_id not in AGENTS:
        raise KeyError(agent_id)
    hits = rag.retrieve(db, user_id, text) if use_rag else []
    context, citations = rag.build_context(hits)
    system = AGENTS[agent_id][1] + (f"\n\nContext:\n{context}" if context else "")
    output = get_provider(provider).complete(
        [{"role": "system", "content": system}, {"role": "user", "content": text}])
    db.add(AgentLog(user_id=user_id, agent_id=agent_id, input=text, output=output))
    db.commit()
    return {"agent_id": agent_id, "output": output, "citations": citations}

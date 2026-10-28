from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..ai import agents, embeddings, rag
from ..ai.providers import ProviderError, get_provider
from ..database import get_db
from ..dependencies import get_current_user
from ..models import AgentLog, ChatMessage, Document, User

router = APIRouter(prefix="/api", tags=["ai"])


class ExecuteIn(BaseModel):
    input: str = Field(min_length=1, max_length=20000)
    provider: str | None = None


class ChatIn(BaseModel):
    message: str = Field(min_length=1, max_length=20000)
    provider: str | None = None


class TextsIn(BaseModel):
    texts: list[str] = Field(min_length=1, max_length=100)
    provider: str | None = None


class SearchIn(BaseModel):
    query: str = Field(min_length=1, max_length=500)
    limit: int = Field(default=5, ge=1, le=50)


def _run(db, user, agent_id, body: ExecuteIn):
    try:
        return agents.execute(db, user.id, agent_id, body.input, body.provider)
    except KeyError:
        raise HTTPException(404, "Unknown agent")
    except ProviderError as e:
        raise HTTPException(502, str(e))


@router.get("/agents")
def list_agents(user: User = Depends(get_current_user)):
    return agents.list_agents()


for _aid in ("research", "code", "architect", "security"):
    def _mk(aid):
        def endpoint(body: ExecuteIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
            return _run(db, user, aid, body)
        return endpoint
    router.add_api_route(f"/agents/{_aid}", _mk(_aid), methods=["POST"], name=f"agent_{_aid}")


@router.post("/agents/{agent_id}/execute")
def execute_agent(agent_id: str, body: ExecuteIn, user: User = Depends(get_current_user),
                  db: Session = Depends(get_db)):
    return _run(db, user, agent_id, body)


@router.get("/agents/{agent_id}/logs")
def agent_logs(agent_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = db.scalars(select(AgentLog).where(AgentLog.user_id == user.id, AgentLog.agent_id == agent_id)
                      .order_by(AgentLog.id.desc()).limit(100))
    return [{"id": r.id, "input": r.input, "output": r.output, "created_at": r.created_at} for r in rows]


def _chat_messages(db, user, message):
    hist = list(db.scalars(select(ChatMessage).where(ChatMessage.user_id == user.id)
                           .order_by(ChatMessage.id.desc()).limit(10)))[::-1]
    context, citations = rag.build_context(rag.retrieve(db, user.id, message, 3))
    sys = "You are Onoma AI." + (f"\n\nContext:\n{context}" if context else "")
    msgs = [{"role": "system", "content": sys}] + [{"role": h.role, "content": h.content} for h in hist]
    return msgs + [{"role": "user", "content": message}], citations


@router.post("/chat")
def chat(body: ChatIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    msgs, citations = _chat_messages(db, user, body.message)
    try:
        reply = get_provider(body.provider).complete(msgs)
    except ProviderError as e:
        raise HTTPException(502, str(e))
    db.add_all([ChatMessage(user_id=user.id, role="user", content=body.message),
                ChatMessage(user_id=user.id, role="assistant", content=reply)])
    db.commit()
    return {"reply": reply, "citations": citations}


@router.post("/chat/stream")
def chat_stream(body: ChatIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    msgs, _ = _chat_messages(db, user, body.message)
    try:
        provider = get_provider(body.provider)
    except ProviderError as e:
        raise HTTPException(502, str(e))

    def gen():
        for part in provider.stream(msgs):
            yield part

    return StreamingResponse(gen(), media_type="text/plain")


@router.get("/chat/history")
def chat_history(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = db.scalars(select(ChatMessage).where(ChatMessage.user_id == user.id)
                      .order_by(ChatMessage.id.desc()).limit(100))
    return [{"role": r.role, "content": r.content, "created_at": r.created_at} for r in rows][::-1]


@router.post("/embeddings/generate")
def generate(body: TextsIn, user: User = Depends(get_current_user)):
    return {"embeddings": embeddings.embed_texts(body.texts, body.provider)}


@router.post("/embeddings/batch")
def batch(body: TextsIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    vecs = embeddings.embed_texts(body.texts, body.provider or "hash")
    ids = []
    for i, (t, v) in enumerate(zip(body.texts, vecs)):
        d = Document(user_id=user.id, name=f"doc-{i}", content=t, embedding=embeddings.dumps(v))
        db.add(d)
        db.flush()
        ids.append(d.id)
    db.commit()
    return {"document_ids": ids}


@router.post("/embeddings/search")
def search(body: SearchIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return rag.retrieve(db, user.id, body.query, body.limit)

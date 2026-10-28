"""Chat API (with streaming)."""
import json

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from ..dependencies import Container, get_container, get_current_user
from ..models.schemas import ChatRequest, Conversation, User

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("")
async def chat(req: ChatRequest, user: User = Depends(get_current_user), c: Container = Depends(get_container)):
    conv, reply = await c.chat.chat(user, req)
    return {"conversation_id": conv.id, "reply": reply}


@router.post("/stream")
async def chat_stream(req: ChatRequest, user: User = Depends(get_current_user),
                      c: Container = Depends(get_container)):
    conv, chunks = await c.chat.stream(user, req)

    async def events():
        yield f"event: meta\ndata: {json.dumps({'conversation_id': conv.id})}\n\n"
        async for chunk in chunks:
            yield f"data: {json.dumps({'content': chunk})}\n\n"
        yield "data: [DONE]\n\n"
    return StreamingResponse(events(), media_type="text/event-stream")


@router.get("/conversations", response_model=list[Conversation])
def conversations(user: User = Depends(get_current_user), c: Container = Depends(get_container)):
    return c.chat.list_conversations(user)


@router.get("/conversations/{conversation_id}", response_model=Conversation)
def conversation(conversation_id: str, user: User = Depends(get_current_user), c: Container = Depends(get_container)):
    return c.chat.get_conversation(user, conversation_id)


@router.delete("/conversations/{conversation_id}", status_code=204)
def delete_conversation(conversation_id: str, user: User = Depends(get_current_user),
                        c: Container = Depends(get_container)):
    c.chat.delete_conversation(user, conversation_id)

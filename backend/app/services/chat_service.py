"""Chat with conversation history and optional RAG."""
from __future__ import annotations

from typing import AsyncIterator

from ..ai import rag
from ..ai.providers import get_provider
from ..db.repositories import Repositories
from ..models.schemas import ChatRequest, Conversation, Message, User
from ..utils.exceptions import NotFound
from .workspace_service import WorkspaceService

SYSTEM_PROMPT = "You are Onoma AI, a helpful assistant inside the Onoma AI Genesis platform."
HISTORY_LIMIT = 20


class ChatService:
    def __init__(self, repos: Repositories, workspaces: WorkspaceService):
        self.repos = repos
        self.workspaces = workspaces

    def get_conversation(self, user: User, conversation_id: str) -> Conversation:
        conv = self.repos.conversations.get(conversation_id)
        if conv is None or conv.user_id != user.id:
            raise NotFound("Conversation not found")
        return conv

    def list_conversations(self, user: User) -> list[Conversation]:
        return self.repos.conversations.for_user(user.id)

    def delete_conversation(self, user: User, conversation_id: str) -> None:
        self.get_conversation(user, conversation_id)
        self.repos.conversations.delete(conversation_id)

    async def _prepare(self, user: User, req: ChatRequest) -> tuple[Conversation, list[dict]]:
        if req.workspace_id:
            self.workspaces.get(user, req.workspace_id)
        if req.conversation_id:
            conv = self.get_conversation(user, req.conversation_id)
        else:
            conv = self.repos.conversations.create(Conversation(
                user_id=user.id, workspace_id=req.workspace_id, title=req.message[:60]))
        system = SYSTEM_PROMPT
        if req.use_rag and (req.workspace_id or conv.workspace_id):
            docs = self.repos.documents.for_workspace(req.workspace_id or conv.workspace_id)
            context = rag.build_context(await rag.retrieve(req.message, docs))
            if context:
                system += f"\n\nUse this context from the user's documents:\n{context}"
        history = [{"role": m.role, "content": m.content} for m in conv.messages[-HISTORY_LIMIT:]]
        messages = [{"role": "system", "content": system}, *history, {"role": "user", "content": req.message}]
        return conv, messages

    def _save(self, conv: Conversation, user_text: str, reply: str) -> Conversation:
        msgs = [*conv.messages, Message(role="user", content=user_text), Message(role="assistant", content=reply)]
        return self.repos.conversations.update(conv.id, messages=msgs)

    async def chat(self, user: User, req: ChatRequest) -> tuple[Conversation, str]:
        conv, messages = await self._prepare(user, req)
        reply = await get_provider(req.provider).chat(messages)
        return self._save(conv, req.message, reply), reply

    async def stream(self, user: User, req: ChatRequest) -> tuple[Conversation, AsyncIterator[str]]:
        conv, messages = await self._prepare(user, req)
        provider = get_provider(req.provider)

        async def gen() -> AsyncIterator[str]:
            parts: list[str] = []
            try:
                async for chunk in provider.stream(messages):
                    parts.append(chunk)
                    yield chunk
            finally:
                if parts:
                    self._save(conv, req.message, "".join(parts))
        return conv, gen()

"""Route registration."""
from fastapi import APIRouter

from . import (
    agents, audit, auth, automations, chat, documents, embeddings, memory,
    organizations, projects, search, tasks, users, workspaces,
)

api_router = APIRouter()
for module in (auth, users, organizations, workspaces, projects, documents, tasks, agents,
               automations, memory, search, chat, embeddings, audit):
    api_router.include_router(module.router)

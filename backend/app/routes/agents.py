"""Agent management and execution API."""
from fastapi import APIRouter, Depends

from ..ai.tools import registry
from ..dependencies import Container, get_container, get_current_user
from ..models.schemas import Agent, AgentCreate, AgentRunRequest, AgentUpdate, User

router = APIRouter(prefix="/agents", tags=["agents"])


@router.get("/tools")
def list_tools(_: User = Depends(get_current_user)):
    return [registry.get(n).schema() for n in registry.names()]


@router.post("", response_model=Agent, status_code=201)
def create(data: AgentCreate, user: User = Depends(get_current_user), c: Container = Depends(get_container)):
    agent = c.agents.create(user, data)
    c.audit.record(user.id, "agent.create", f"agent:{agent.id}")
    return agent


@router.get("", response_model=list[Agent])
def list_agents(workspace_id: str, user: User = Depends(get_current_user), c: Container = Depends(get_container)):
    return c.agents.list(user, workspace_id)


@router.get("/{agent_id}", response_model=Agent)
def get(agent_id: str, user: User = Depends(get_current_user), c: Container = Depends(get_container)):
    return c.agents.get(user, agent_id)


@router.patch("/{agent_id}", response_model=Agent)
def update(agent_id: str, data: AgentUpdate, user: User = Depends(get_current_user),
           c: Container = Depends(get_container)):
    return c.agents.update(user, agent_id, data)


@router.delete("/{agent_id}", status_code=204)
def delete(agent_id: str, user: User = Depends(get_current_user), c: Container = Depends(get_container)):
    c.agents.delete(user, agent_id)


@router.post("/{agent_id}/run")
async def run(agent_id: str, data: AgentRunRequest, user: User = Depends(get_current_user),
              c: Container = Depends(get_container)):
    result = await c.agents.run(user, agent_id, data.input, data.max_steps)
    c.audit.record(user.id, "agent.run", f"agent:{agent_id}")
    return result

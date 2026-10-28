"""Agents and automations; agent execution."""
from __future__ import annotations

from ..ai.agents import AgentRunner
from ..models.schemas import Agent, AgentCreate, Automation, AutomationCreate, User
from ..utils.exceptions import BadRequest
from ._scoped import ScopedService
from ..ai.tools import registry


class AgentService(ScopedService):
    repo_name, label = "agents", "Agent"

    def create(self, user: User, data: AgentCreate) -> Agent:
        unknown = [t for t in data.tools if registry.get(t) is None]
        if unknown:
            raise BadRequest(f"Unknown tools: {', '.join(unknown)}")
        return self._create(user, Agent, data)

    async def run(self, user: User, agent_id: str, user_input: str, max_steps: int = 5) -> dict:
        agent = self.get(user, agent_id)
        runner = AgentRunner(agent.system_prompt, agent.tools, agent.provider, agent.model)
        result = await runner.run(user_input, max_steps)
        return {"output": result.output,
                "steps": [{"tool": s.tool, "args": s.args, "observation": s.observation} for s in result.steps]}


class AutomationService(ScopedService):
    repo_name, label = "automations", "Automation"

    def create(self, user: User, data: AutomationCreate) -> Automation:
        return self._create(user, Automation, data)

"""Agent execution framework: a bounded JSON tool-calling loop."""
import json
from dataclasses import dataclass, field

from .providers import get_provider
from .tools import Tool, registry


@dataclass
class AgentStep:
    thought: str
    tool: str | None = None
    args: dict = field(default_factory=dict)
    observation: str | None = None


@dataclass
class AgentResult:
    output: str
    steps: list[AgentStep]


def _parse_tool_call(text: str) -> dict | None:
    text = text.strip()
    if not text.startswith("{"):
        return None
    try:
        data = json.loads(text)
    except ValueError:
        return None
    return data if isinstance(data, dict) and "tool" in data else None


class AgentRunner:
    def __init__(self, system_prompt: str, tool_names: list[str] | None = None,
                 provider: str | None = None, model: str | None = None):
        self.system_prompt = system_prompt
        self.tools: list[Tool] = registry.subset(tool_names or [])
        self.provider = get_provider(provider)
        self.model = model

    def _system(self) -> str:
        if not self.tools:
            return self.system_prompt
        specs = json.dumps([t.schema() for t in self.tools])
        return (f"{self.system_prompt}\n\nTools available: {specs}\n"
                'To call a tool reply ONLY with JSON: {"tool": "<name>", "args": {...}}. '
                "Otherwise reply with the final answer in plain text.")

    async def run(self, user_input: str, max_steps: int = 5) -> AgentResult:
        messages = [{"role": "system", "content": self._system()},
                    {"role": "user", "content": user_input}]
        steps: list[AgentStep] = []
        for _ in range(max_steps):
            reply = await self.provider.chat(messages, model=self.model)
            call = _parse_tool_call(reply) if self.tools else None
            if call is None:
                return AgentResult(reply, steps)
            tool = next((t for t in self.tools if t.name == call["tool"]), None)
            args = call.get("args") if isinstance(call.get("args"), dict) else {}
            try:
                obs = tool.run(**args) if tool else f"Unknown tool: {call['tool']}"
            except Exception as exc:  # noqa: BLE001 - tool errors are fed back to the model
                obs = f"Tool error: {exc}"
            steps.append(AgentStep(reply, call["tool"], args, obs))
            messages += [{"role": "assistant", "content": reply},
                         {"role": "user", "content": f"Tool result: {obs}"}]
        return AgentResult("Stopped: maximum steps reached", steps)

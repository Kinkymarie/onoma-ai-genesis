import asyncio
import json

from app.ai.agents import AgentRunner
from app.ai.providers.base import LLMProvider
from app.ai.tools import safe_eval
import pytest


class ScriptedProvider(LLMProvider):
    def __init__(self, replies):
        self.replies = list(replies)

    async def chat(self, messages, **kw):
        return self.replies.pop(0)

    async def stream(self, messages, **kw):
        yield self.replies.pop(0)


def runner_with(replies, tools):
    r = AgentRunner("sys", tools, "echo")
    r.provider = ScriptedProvider(replies)
    return r


def test_safe_eval():
    assert safe_eval("2*(3+4)") == 14
    for bad in ("__import__('os')", "2**1000", "a+1"):
        with pytest.raises(Exception):
            safe_eval(bad)


def test_agent_tool_loop():
    r = runner_with([json.dumps({"tool": "calculator", "args": {"expression": "6*7"}}), "The answer is 42"],
                    ["calculator"])
    result = asyncio.run(r.run("what is 6*7"))
    assert result.output == "The answer is 42"
    assert result.steps[0].observation == "42"


def test_agent_handles_tool_errors_and_max_steps():
    call = json.dumps({"tool": "calculator", "args": {"expression": "1/0"}})
    result = asyncio.run(runner_with([call] * 2, ["calculator"]).run("x", max_steps=2))
    assert result.output.startswith("Stopped")
    assert result.steps[0].observation.startswith("Tool error")


def test_agent_api(client, auth_headers, workspace):
    h = auth_headers
    a = client.post("/api/agents", json={"workspace_id": workspace["id"], "name": "Bot", "tools": ["calculator"]},
                    headers=h)
    assert a.status_code == 201
    r = client.post(f"/api/agents/{a.json()['id']}/run", json={"input": "hi"}, headers=h).json()
    assert r["output"] == "Echo: hi"
    assert client.post("/api/agents", json={"workspace_id": workspace["id"], "name": "B", "tools": ["rm_rf"]},
                       headers=h).status_code == 400
    assert any(t["name"] == "calculator" for t in client.get("/api/agents/tools", headers=h).json())


def test_automation_crud(client, auth_headers, workspace):
    h = auth_headers
    a = client.post("/api/automations", json={"workspace_id": workspace["id"], "name": "A", "trigger": "task.done"},
                    headers=h).json()
    assert client.patch(f"/api/automations/{a['id']}", json={"enabled": False}, headers=h).json()["enabled"] is False
    assert client.delete(f"/api/automations/{a['id']}", headers=h).status_code == 204

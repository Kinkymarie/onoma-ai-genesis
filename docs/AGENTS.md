# Agents

An agent is a system prompt plus an allow-list of tools, optionally pinned to a provider/model.
`POST /api/agents/{id}/run` runs a bounded loop (`max_steps`, default 5, max 10):
the model either replies with plain text (the final answer) or with JSON `{"tool": "<name>", "args": {...}}`;
the tool result is fed back and the loop continues. Tool errors are returned to the model, not raised.

Built-in tools (`GET /api/agents/tools`): `calculator` (AST-based, no `eval`), `current_time`, `word_count`.
Register more with `app.ai.tools.registry.register(Tool(...))`.

"""Tool / function definitions usable by agents."""
import ast
import operator
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable

_OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
        ast.Div: operator.truediv, ast.Pow: operator.pow, ast.Mod: operator.mod,
        ast.USub: operator.neg, ast.UAdd: operator.pos}


def safe_eval(expr: str) -> float:
    """Evaluate arithmetic without ``eval``."""
    def ev(node):
        if isinstance(node, ast.Expression):
            return ev(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)) \
                and not isinstance(node.value, bool):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
            left, right = ev(node.left), ev(node.right)
            if isinstance(node.op, ast.Pow) and abs(right) > 100:
                raise ValueError("exponent too large")
            return _OPS[type(node.op)](left, right)
        if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
            return _OPS[type(node.op)](ev(node.operand))
        raise ValueError("unsupported expression")
    if len(expr) > 200:
        raise ValueError("expression too long")
    return ev(ast.parse(expr, mode="eval"))


@dataclass
class Tool:
    name: str
    description: str
    func: Callable[..., Any]
    parameters: dict[str, str] = field(default_factory=dict)

    def schema(self) -> dict:
        return {"name": self.name, "description": self.description, "parameters": self.parameters}

    def run(self, **kwargs) -> str:
        return str(self.func(**kwargs))


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> Tool:
        self._tools[tool.name] = tool
        return tool

    def get(self, name: str) -> Tool | None:
        return self._tools.get(name)

    def names(self) -> list[str]:
        return sorted(self._tools)

    def subset(self, names: list[str]) -> list[Tool]:
        return [self._tools[n] for n in names if n in self._tools]


registry = ToolRegistry()
registry.register(Tool("calculator", "Evaluate an arithmetic expression", lambda expression: safe_eval(expression),
                       {"expression": "arithmetic expression, e.g. 2*(3+4)"}))
registry.register(Tool("current_time", "Current UTC time in ISO format",
                       lambda: datetime.now(timezone.utc).isoformat()))
registry.register(Tool("word_count", "Count words in text", lambda text: len(str(text).split()),
                       {"text": "text to count"}))

"""Response formatting helpers."""
import math
from typing import Any, Sequence


def success(data: Any = None, message: str | None = None) -> dict:
    body: dict[str, Any] = {"success": True, "data": data}
    if message:
        body["message"] = message
    return body


def error(code: str, message: str) -> dict:
    return {"success": False, "error": {"code": code, "message": message}}


def paginate(items: Sequence, page: int = 1, page_size: int = 20) -> dict:
    page = max(page, 1)
    page_size = max(page_size, 1)
    total = len(items)
    start = (page - 1) * page_size
    return {
        "items": list(items[start:start + page_size]),
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": math.ceil(total / page_size) if total else 0,
    }

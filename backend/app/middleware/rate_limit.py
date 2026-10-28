"""Fixed-window in-memory rate limiting per client IP."""
import threading
import time

from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from ..utils.formatters import error


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, limit_per_minute: int = 120):
        super().__init__(app)
        self.limit = limit_per_minute
        self._hits: dict[str, tuple[int, int]] = {}
        self._lock = threading.Lock()

    async def dispatch(self, request, call_next):
        if self.limit <= 0 or request.url.path == "/health":
            return await call_next(request)
        key = request.client.host if request.client else "unknown"
        window = int(time.time() // 60)
        with self._lock:
            if len(self._hits) > 10000:
                self._hits = {k: v for k, v in self._hits.items() if v[0] == window}
            w, count = self._hits.get(key, (window, 0))
            count = count + 1 if w == window else 1
            self._hits[key] = (window, count)
        if count > self.limit:
            return JSONResponse(error("rate_limited", "Too many requests"), status_code=429,
                                headers={"Retry-After": "60"})
        return await call_next(request)

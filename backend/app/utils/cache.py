"""Small thread-safe TTL cache."""
import threading
import time
from typing import Any, Callable


class TTLCache:
    def __init__(self, default_ttl: float = 300.0):
        self.default_ttl = default_ttl
        self._data: dict[str, tuple[float, Any]] = {}
        self._lock = threading.Lock()

    def set(self, key: str, value: Any, ttl: float | None = None) -> None:
        with self._lock:
            self._data[key] = (time.monotonic() + (self.default_ttl if ttl is None else ttl), value)

    def get(self, key: str, default: Any = None) -> Any:
        with self._lock:
            item = self._data.get(key)
            if item is None:
                return default
            expires, value = item
            if expires <= time.monotonic():
                del self._data[key]
                return default
            return value

    def delete(self, key: str) -> None:
        with self._lock:
            self._data.pop(key, None)

    def purge(self) -> int:
        now = time.monotonic()
        with self._lock:
            expired = [k for k, (exp, _) in self._data.items() if exp <= now]
            for k in expired:
                del self._data[k]
            return len(expired)

    def clear(self) -> None:
        with self._lock:
            self._data.clear()

    def get_or_set(self, key: str, factory: Callable[[], Any], ttl: float | None = None) -> Any:
        sentinel = object()
        value = self.get(key, sentinel)
        if value is sentinel:
            value = factory()
            self.set(key, value, ttl)
        return value

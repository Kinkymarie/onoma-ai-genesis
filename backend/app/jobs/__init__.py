"""Background jobs: a small in-process scheduler (swap for Celery/APScheduler in production)."""
import threading
from typing import Callable

from ..utils.logger import get_logger

log = get_logger(__name__)


class JobRunner:
    def __init__(self) -> None:
        self._jobs: dict[str, tuple[Callable[[], object], float]] = {}
        self._stop = threading.Event()
        self._threads: list[threading.Thread] = []

    def register(self, name: str, func: Callable[[], object], interval_seconds: float) -> None:
        self._jobs[name] = (func, interval_seconds)

    def run_now(self, name: str):
        func, _ = self._jobs[name]
        try:
            return func()
        except Exception:  # noqa: BLE001 - jobs must never kill the scheduler
            log.exception("job failed", extra={"job": name})

    def start(self) -> None:
        self._stop.clear()
        for name, (_, interval) in self._jobs.items():
            t = threading.Thread(target=self._loop, args=(name, interval), daemon=True, name=f"job-{name}")
            t.start()
            self._threads.append(t)

    def _loop(self, name: str, interval: float) -> None:
        while not self._stop.wait(interval):
            self.run_now(name)

    def stop(self) -> None:
        self._stop.set()
        for t in self._threads:
            t.join(timeout=2)
        self._threads.clear()


runner = JobRunner()

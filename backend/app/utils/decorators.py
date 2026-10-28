"""Common decorators."""
import functools
import inspect
import time

from .logger import get_logger

log = get_logger(__name__)


def timed(func):
    """Log execution time of sync or async callables."""
    if inspect.iscoroutinefunction(func):
        @functools.wraps(func)
        async def awrapper(*args, **kwargs):
            start = time.perf_counter()
            try:
                return await func(*args, **kwargs)
            finally:
                log.debug("timed", extra={"func": func.__name__, "ms": (time.perf_counter() - start) * 1000})
        return awrapper

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        try:
            return func(*args, **kwargs)
        finally:
            log.debug("timed", extra={"func": func.__name__, "ms": (time.perf_counter() - start) * 1000})
    return wrapper


def retry(times: int = 3, delay: float = 0.1, exceptions: tuple = (Exception,)):
    """Retry a sync callable with linear backoff."""
    def deco(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, times + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions:
                    if attempt == times:
                        raise
                    time.sleep(delay * attempt)
        return wrapper
    return deco

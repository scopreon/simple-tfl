import inspect
import time
from collections.abc import Callable
from dataclasses import dataclass
from functools import wraps
from threading import Lock
from typing import ParamSpec, TypeVar


T = TypeVar("T")
P = ParamSpec("P")


@dataclass(slots=True)
class CacheEntry[T]:
    creation_time: float
    result: T


# this is NOT thread safe
def cache_with_ttl(*, ttl: float) -> Callable[[Callable[P, T]], Callable[P, T]]:
    def decorator(f: Callable[P, T]) -> Callable[P, T]:
        mutex_lock = Lock()

        _results: dict[tuple, CacheEntry[T]] = {}
        sig = inspect.signature(f)

        @wraps(f)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            current_epoch = time.monotonic()

            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()

            hashed = tuple((name, bound.arguments[name]) for name in sig.parameters)

            with mutex_lock:
                entry = _results.get(hashed)
                if entry and entry.creation_time + ttl > current_epoch:
                    return entry.result

            ret = f(*args, **kwargs)

            with mutex_lock:
                entry = _results.get(hashed)
                if entry and entry.creation_time + ttl > current_epoch:
                    return entry.result
                _results[hashed] = CacheEntry(creation_time=current_epoch, result=ret)

            return ret

        return wrapper

    return decorator

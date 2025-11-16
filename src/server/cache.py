import inspect
import time
from collections.abc import Callable
from dataclasses import dataclass
from functools import wraps
from typing import ParamSpec, TypeVar


T = TypeVar("T")
P = ParamSpec("P")


@dataclass(slots=True)
class CacheEntry[T]:
    creation_time: float
    result: T


kwd_mark = (
    object()
)  # https://stackoverflow.com/questions/10220599/how-to-hash-args-kwargs-for-function-cache


# this is NOT thread safe
def cache_with_ttl(*, ttl: float) -> Callable[[Callable[P, T]], Callable[P, T]]:
    def decorator(f: Callable[P, T]) -> Callable[P, T]:
        _results: dict[tuple, CacheEntry[T]] = {}
        sig = inspect.signature(f)

        @wraps(f)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            current_epoch = time.time()

            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()

            hashed = tuple((name, bound.arguments[name]) for name in sig.parameters)

            if hashed in _results:
                if _results[hashed].creation_time + ttl > current_epoch:
                    return _results[hashed].result
                _results.pop(hashed)

            ret = f(*args, **kwargs)
            _results[hashed] = CacheEntry(creation_time=current_epoch, result=ret)
            return ret

        return wrapper

    return decorator

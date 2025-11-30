import inspect
import time
from collections.abc import Callable, Coroutine
from dataclasses import dataclass
from functools import update_wrapper
from threading import Lock
from typing import ParamSpec, TypeVar


P = ParamSpec("P")
T = TypeVar("T")
T_co = TypeVar("T_co", covariant=True)


@dataclass(slots=True)
class CacheEntry[T]:
    creation_time: float
    result: T


class CachedFunction[**P, T_co]:
    __name__: str

    def __init__(self, f: Callable[P, T_co], ttl: float) -> None:
        self._f = f
        self._ttl = ttl
        self._sig = inspect.signature(f)
        self._cache: dict[tuple, CacheEntry[T_co]] = {}
        self._lock = Lock()

        update_wrapper(self, f)

    def clear_cache(self) -> None:
        with self._lock:
            self._cache.clear()

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> T_co:
        now = time.monotonic()

        bound = self._sig.bind(*args, **kwargs)
        bound.apply_defaults()
        hashed = tuple(
            (
                name,
                bound.arguments[name]
                if name != "kwargs"
                else tuple((value, key) for value, key in sorted(bound.arguments[name].items())),
            )
            for name in self._sig.parameters
        )

        with self._lock:
            entry = self._cache.get(hashed)
            if entry and entry.creation_time + self._ttl > now:
                return entry.result

        result = self._f(*args, **kwargs)

        with self._lock:
            entry = self._cache.get(hashed)
            if entry and entry.creation_time + self._ttl > now:
                return entry.result
            self._cache[hashed] = CacheEntry(now, result)

        return result


class CachedAsyncFunction[**P, T_co]:
    __name__: str

    def __init__(self, f: Callable[P, Coroutine[None, None, T_co]], ttl: float) -> None:
        self._f = f
        self._ttl = ttl
        self._sig = inspect.signature(f)
        self._cache: dict[tuple, CacheEntry[T_co]] = {}
        self._lock = Lock()

        update_wrapper(self, f)
        inspect.markcoroutinefunction(self)  # maybe a hack

    def clear_cache(self) -> None:
        with self._lock:
            self._cache.clear()

    async def __call__(self, *args: P.args, **kwargs: P.kwargs) -> T_co:
        now = time.monotonic()

        bound = self._sig.bind(*args, **kwargs)
        bound.apply_defaults()
        hashed = tuple(
            (
                name,
                bound.arguments[name]
                if name != "kwargs"
                else tuple((value, key) for value, key in sorted(bound.arguments[name].items())),
            )
            for name in self._sig.parameters
        )

        with self._lock:
            entry = self._cache.get(hashed)
            if entry and entry.creation_time + self._ttl > now:
                return entry.result

        result = await self._f(*args, **kwargs)

        with self._lock:
            entry = self._cache.get(hashed)
            if entry and entry.creation_time + self._ttl > now:
                return entry.result
            self._cache[hashed] = CacheEntry(now, result)

        return result


def cache_with_ttl(*, ttl: float) -> Callable[[Callable[P, T_co]], CachedFunction[P, T_co]]:
    def decorator(f: Callable[P, T_co]) -> CachedFunction[P, T_co]:
        return CachedFunction(f, ttl)

    return decorator


def aio_cache_with_ttl(
    *, ttl: float
) -> Callable[[Callable[P, Coroutine[None, None, T_co]]], CachedAsyncFunction[P, T_co]]:
    def decorator(
        f: Callable[P, Coroutine[None, None, T_co]],
    ) -> CachedAsyncFunction[P, T_co]:
        return CachedAsyncFunction(f, ttl)

    return decorator

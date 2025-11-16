import datetime
import inspect

import pytest
from freezegun import freeze_time

from src.server.cache import aio_cache_with_ttl


@pytest.mark.asyncio
async def test_function_caches_async() -> None:
    counter = 0

    @aio_cache_with_ttl(ttl=1)
    async def f() -> None:
        nonlocal counter
        counter += 1

    initial_datetime = datetime.datetime(year=2000, month=7, day=12, hour=15)
    with freeze_time(initial_datetime):
        assert counter == 0
        await f()
        assert counter == 1
        await f()
        assert counter == 1


@pytest.mark.asyncio
async def test_function_caches_until_ttl_async() -> None:
    counter = 0

    @aio_cache_with_ttl(ttl=1)
    async def f() -> None:
        nonlocal counter
        counter += 1

    initial_datetime = datetime.datetime(year=2000, month=7, day=12, hour=15)
    with freeze_time(initial_datetime) as frozen:
        assert counter == 0
        await f()
        assert counter == 1
        await f()
        assert counter == 1

        frozen.tick(delta=2)
        await f()
        assert counter == 2
        await f()
        assert counter == 2


@pytest.mark.asyncio
async def test_cache_respects_args_and_kwargs_async() -> None:
    counter = 0

    @aio_cache_with_ttl(ttl=10)
    async def add(a: int, b: int = 0) -> int:
        nonlocal counter
        counter += 1
        return a + b

    initial_datetime = datetime.datetime(year=2020, month=1, day=1)
    with freeze_time(initial_datetime):
        # different positional args -> different cache entries
        assert await add(1, 2) == 3
        assert counter == 1
        assert await add(1, 2) == 3
        assert counter == 1

        # different kwargs order should be treated the same (sorted in hash)
        assert await add(a=2, b=3) == 5
        assert counter == 2
        assert await add(b=3, a=2) == 5
        assert counter == 2

        # mixing args and kwargs that represent same call -> same cache key
        assert await add(2, b=3) == 5
        assert counter == 2


@pytest.mark.asyncio
async def test_zero_ttl_does_not_cache_async() -> None:
    counter = 0

    @aio_cache_with_ttl(ttl=0)
    async def g() -> int:
        nonlocal counter
        counter += 1
        return counter

    initial_datetime = datetime.datetime(year=2021, month=6, day=1)
    with freeze_time(initial_datetime):
        assert await g() == 1
        assert await g() == 2
        assert await g() == 3


@pytest.mark.asyncio
async def test_separate_functions_have_separate_caches_async() -> None:
    c1 = 0
    c2 = 0

    @aio_cache_with_ttl(ttl=10)
    async def f1(x: int) -> int:
        nonlocal c1
        c1 += 1
        return x + 1

    @aio_cache_with_ttl(ttl=10)
    async def f2(x: int) -> int:
        nonlocal c2
        c2 += 1
        return x + 2

    initial_datetime = datetime.datetime(year=2022, month=3, day=3)
    with freeze_time(initial_datetime):
        assert await f1(1) == 2
        assert c1 == 1
        assert await f1(1) == 2
        assert c1 == 1

        assert await f2(1) == 3
        assert c2 == 1
        assert await f2(1) == 3
        assert c2 == 1


@pytest.mark.asyncio
async def test_return_value_none_is_cached_async() -> None:
    counter = 0

    @aio_cache_with_ttl(ttl=5)
    async def maybe_none(flag: bool) -> None | int:
        nonlocal counter
        counter += 1
        return None if flag else counter

    initial_datetime = datetime.datetime(year=2022, month=8, day=8)
    with freeze_time(initial_datetime):
        assert await maybe_none(True) is None
        assert counter == 1
        # second call with same arg should not increase counter
        assert await maybe_none(True) is None
        assert counter == 1

        # different arg leads to new computation
        assert await maybe_none(False) == 2
        assert counter == 2
        assert await maybe_none(False) == 2
        assert counter == 2


def test_decorator_preserves_function_metadata_async() -> None:
    @aio_cache_with_ttl(ttl=1)
    async def original(a: int) -> int:
        """docstring"""
        return a

    # metadata should be preserved on the wrapper
    assert original.__name__ == "original"
    assert original.__doc__ == "docstring"
    assert inspect.iscoroutinefunction(original)


@pytest.mark.asyncio
async def test_function_caches_with_clear_async() -> None:
    counter = 0

    @aio_cache_with_ttl(ttl=1)
    async def f() -> None:
        nonlocal counter
        counter += 1

    initial_datetime = datetime.datetime(year=2000, month=7, day=12, hour=15)
    with freeze_time(initial_datetime):
        assert counter == 0
        await f()
        assert counter == 1
        f.clear_cache()
        await f()
        assert counter == 2

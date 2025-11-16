import datetime

from freezegun import freeze_time

from src.server.cache import cache_with_ttl


def test_function_caches() -> None:
    counter = 0

    @cache_with_ttl(ttl=1)
    def f() -> None:
        nonlocal counter
        counter += 1

    initial_datetime = datetime.datetime(year=2000, month=7, day=12, hour=15)
    with freeze_time(initial_datetime):
        assert counter == 0
        f()
        assert counter == 1
        f()
        assert counter == 1


def test_function_caches_until_ttl() -> None:
    counter = 0

    @cache_with_ttl(ttl=1)
    def f() -> None:
        nonlocal counter
        counter += 1

    initial_datetime = datetime.datetime(year=2000, month=7, day=12, hour=15)
    with freeze_time(initial_datetime) as frozen:
        assert counter == 0
        f()
        assert counter == 1
        f()
        assert counter == 1

        frozen.tick(delta=2)
        f()
        assert counter == 2
        f()
        assert counter == 2


def test_cache_respects_args_and_kwargs() -> None:
    counter = 0

    @cache_with_ttl(ttl=10)
    def add(a: int, b: int = 0) -> int:
        nonlocal counter
        counter += 1
        return a + b

    initial_datetime = datetime.datetime(year=2020, month=1, day=1)
    with freeze_time(initial_datetime):
        # different positional args -> different cache entries
        assert add(1, 2) == 3
        assert counter == 1
        assert add(1, 2) == 3
        assert counter == 1

        # different kwargs order should be treated the same (sorted in hash)
        assert add(a=2, b=3) == 5
        assert counter == 2
        assert add(b=3, a=2) == 5
        assert counter == 2

        # mixing args and kwargs that represent same call -> same cache key
        assert add(2, b=3) == 5
        assert counter == 2


def test_zero_ttl_does_not_cache() -> None:
    counter = 0

    @cache_with_ttl(ttl=0)
    def g() -> int:
        nonlocal counter
        counter += 1
        return counter

    initial_datetime = datetime.datetime(year=2021, month=6, day=1)
    with freeze_time(initial_datetime):
        assert g() == 1
        assert g() == 2
        assert g() == 3


def test_separate_functions_have_separate_caches() -> None:
    c1 = 0
    c2 = 0

    @cache_with_ttl(ttl=10)
    def f1(x: int) -> int:
        nonlocal c1
        c1 += 1
        return x + 1

    @cache_with_ttl(ttl=10)
    def f2(x: int) -> int:
        nonlocal c2
        c2 += 1
        return x + 2

    initial_datetime = datetime.datetime(year=2022, month=3, day=3)
    with freeze_time(initial_datetime):
        assert f1(1) == 2
        assert c1 == 1
        assert f1(1) == 2
        assert c1 == 1

        assert f2(1) == 3
        assert c2 == 1
        assert f2(1) == 3
        assert c2 == 1


def test_return_value_none_is_cached() -> None:
    counter = 0

    @cache_with_ttl(ttl=5)
    def maybe_none(flag: bool) -> None | int:
        nonlocal counter
        counter += 1
        return None if flag else counter

    initial_datetime = datetime.datetime(year=2022, month=8, day=8)
    with freeze_time(initial_datetime):
        assert maybe_none(True) is None
        assert counter == 1
        # second call with same arg should not increase counter
        assert maybe_none(True) is None
        assert counter == 1

        # different arg leads to new computation
        assert maybe_none(False) == 2
        assert counter == 2
        assert maybe_none(False) == 2
        assert counter == 2


def test_decorator_preserves_function_metadata() -> None:
    @cache_with_ttl(ttl=1)
    def original(a: int) -> int:
        """docstring"""
        return a

    assert original.__name__ == "original"
    assert original.__doc__ == "docstring"

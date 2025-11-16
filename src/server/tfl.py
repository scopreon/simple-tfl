from functools import cache

from ._types import TrainArrival


@cache
async def get_id(station_name: str) -> str:
    raise NotImplementedError()


async def get_arrivals(station_id: str, line: str) -> list[TrainArrival]:
    raise NotImplementedError()

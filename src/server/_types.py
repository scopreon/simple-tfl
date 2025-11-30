from typing import Literal

from pydantic import BaseModel


Direction = Literal["inbound", "outbound", "all"]


class TrainArrival(BaseModel):
    time: int
    destination: str
    via: str


class TrainTimeRequest(BaseModel):
    station: str
    line: str
    destination: str | None
    direction: Direction = "all"


class TrainTimeResponse(BaseModel):
    schedule: list[TrainArrival]


class LineStatusRequest(BaseModel):
    line: str


class LineStatusResponse(BaseModel):
    status: str
    description: str

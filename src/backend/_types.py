from typing import Literal

from pydantic import BaseModel


Direction = Literal["inbound", "outbound", "all"]


class TrainArrival(BaseModel):
    time: int
    destination: str
    via: str


class LineStatusResponse(BaseModel):
    status: str
    description: str

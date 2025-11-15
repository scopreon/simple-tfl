from pydantic import BaseModel


class TrainArrival(BaseModel):
    time: int
    destination: str
    via: str


class TrainTimeRequest(BaseModel):
    station: str
    destination: str
    line: str


class TrainTimeResponse(BaseModel):
    schedule: list[TrainArrival]

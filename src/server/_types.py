from pydantic import BaseModel


class TrainArrival(BaseModel):
    time: int
    destination: str
    via: str


class TrainTimeRequest(BaseModel):
    station: str
    line: str
    destination: str | None


class TrainTimeResponse(BaseModel):
    schedule: list[TrainArrival]

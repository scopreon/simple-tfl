import json
import os
from typing import Any

import requests
from dotenv import load_dotenv
from pydantic import BaseModel, ConfigDict, Field, TypeAdapter

from ._types import Direction, LineStatusResponse, TrainArrival
from .cache import aio_cache_with_ttl


load_dotenv()


_HEADERS = {
    "Cache-Control": "no-cache",
    "app_key": os.getenv("TFL_PRIVATE"),
}


class _TFLTiming(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    countdown_server_adjustment: str = Field(alias="countdownServerAdjustment")
    source: str
    insert: str
    read: str
    sent: str
    received: str


class _TFLArrival(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    operation_type: int = Field(alias="operationType")
    vehicle_id: str = Field(alias="vehicleId")
    naptan_id: str = Field(alias="naptanId")
    station_name: str = Field(alias="stationName")
    line_id: str = Field(alias="lineId")
    line_name: str = Field(alias="lineName")
    platform_name: str = Field(alias="platformName")
    direction: str
    bearing: str
    destination_naptan_id: str = Field(alias="destinationNaptanId")
    destination_name: str = Field(alias="destinationName")
    timestamp: str
    time_to_station: int = Field(alias="timeToStation")
    current_location: str = Field(alias="currentLocation")
    towards: str
    expected_arrival: str = Field(alias="expectedArrival")
    time_to_live: str = Field(alias="timeToLive")
    mode_name: str = Field(alias="modeName")
    timing: _TFLTiming


class _TFLLineStatus(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    status: str = Field(alias="statusSeverityDescription")
    reason: str = ""


class TFLStatus(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    operator: str
    status: str
    message: str
    status_level: int = Field(alias="statusLevel")


TFL_ENDPOINT = "https://api.tfl.gov.uk"


def healthcheck() -> TFLStatus:
    path = "/NetworkStatus"
    r = requests.get(f"{TFL_ENDPOINT}{path}", headers=_HEADERS)
    assert r.status_code == 200
    return TFLStatus.model_validate_json(r.text)


@aio_cache_with_ttl(ttl=9999999)
async def get_id(station_name: str) -> str:
    params = {
        "query": f"{station_name.title()} Underground Station",
        "modes": "tube",
    }
    path = "/StopPoint/Search"
    # TODO make requests.get a promise
    r = requests.get(f"{TFL_ENDPOINT}{path}", params=params, headers=_HEADERS)
    assert r.status_code == 200
    resp: dict[str, Any] = json.loads(r.text)
    assert resp["total"] == 1
    return resp["matches"][0]["id"]


@aio_cache_with_ttl(ttl=2)
async def get_arrivals(
    station_name: str,
    line: str,
    direction: Direction | None = None,
    destination_station: str | None = None,
) -> list[TrainArrival]:
    if direction is None:
        direction = "all"

    params: dict[str, str] = {
        "direction": direction,
    }
    if destination_station is not None:
        params["destinationStationId"] = await get_id(destination_station)

    station_id = await get_id(station_name)
    path = f"/Line/{line}/Arrivals/{station_id}"
    r = requests.get(f"{TFL_ENDPOINT}{path}", params=params, headers=_HEADERS)
    assert r.status_code == 200
    ret = []
    ta = TypeAdapter(list[_TFLArrival])
    for arrival in ta.validate_json(r.text):
        ret.append(
            TrainArrival(
                destination=arrival.destination_name,
                time=arrival.time_to_station,
                via=arrival.towards,
            )
        )
    return ret


@aio_cache_with_ttl(ttl=30)
async def get_line_status(
    line: str,
) -> LineStatusResponse:
    path = f"/Line/{line}/Status"
    r = requests.get(f"{TFL_ENDPOINT}{path}", headers=_HEADERS)
    assert r.status_code == 200

    json_resp = json.loads(r.text)
    temp = _TFLLineStatus.model_validate(json_resp[0]["lineStatuses"][0])
    return LineStatusResponse(status=temp.status, description=temp.reason)

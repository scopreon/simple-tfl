import asyncio

from fastapi import FastAPI, WebSocket
from starlette.websockets import WebSocketDisconnect

from ._types import Direction
from .settings import BACKEND_PORT
from .tfl import get_arrivals, get_line_status


app = FastAPI()


@app.websocket("/ws/arrivals/{station}/{line}")
@app.websocket("/ws/arrivals/{station}/{line}/{direction}")
async def ws_get_arrivals(
    websocket: WebSocket, station: str, line: str, direction: Direction | None = None
) -> None:
    await websocket.accept()
    print("Opened connection")
    try:
        while True:
            raw_data = await get_arrivals(station, line, direction)
            data = [model.model_dump_json() for model in raw_data]
            await websocket.send_text("\n".join(data))
            await asyncio.sleep(2)
    except WebSocketDisconnect:
        print("Closed connection")


@app.websocket("/ws/status/{line}")
async def ws_get_status(
    websocket: WebSocket,
    line: str,
) -> None:
    await websocket.accept()
    print("Opened connection")
    try:
        while True:
            raw_data = await get_line_status(line)
            await websocket.send_text(raw_data.model_dump_json())
            await asyncio.sleep(2)
    except WebSocketDisconnect:
        print("Closed connection")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("src.server.main:app", port=BACKEND_PORT, reload=True)

import asyncio

from fastapi import FastAPI, WebSocket
from starlette.websockets import WebSocketDisconnect

from .tfl import get_arrivals


app = FastAPI()


@app.websocket("/ws/{station}/{line}")
async def websocket_endpoint(websocket: WebSocket, station: str, line: str) -> None:
    await websocket.accept()
    print("Opened connection")
    try:
        while True:
            raw_data = await get_arrivals(station, line)
            data = [model.model_dump_json() for model in raw_data]
            await websocket.send_text("\n".join(data))
            await asyncio.sleep(2)
    except WebSocketDisconnect:
        print("Closed connection")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("src.server.main:app", port=8000, reload=True)

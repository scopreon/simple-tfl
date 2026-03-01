import asyncio
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, WebSocket
from fastapi.responses import FileResponse, Response
from starlette.websockets import WebSocketDisconnect

from ._types import Direction
from .logging import LOGGING_CONFIG
from .settings import (
    BACKEND_PORT,
    CV_PATH,
    CV_SYNC_INTERVAL,
    CV_URL,
)
from .tfl import get_arrivals, get_line_status


logger = logging.getLogger(__name__)


async def _sync_cv() -> None:
    """Download the CV PDF from GitHub on a loop."""
    async with httpx.AsyncClient() as client:
        while True:
            try:
                resp = await client.get(CV_URL, follow_redirects=True)
                resp.raise_for_status()
                CV_PATH.write_bytes(resp.content)
                logger.info("CV synced successfully")
            except Exception:
                logger.exception("Failed to sync CV")
            await asyncio.sleep(CV_SYNC_INTERVAL)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    task = asyncio.create_task(_sync_cv())
    yield
    task.cancel()


app = FastAPI(lifespan=lifespan)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "healthy"}


@app.get("/api/cv", response_model=None)
def get_cv() -> FileResponse | Response:
    if not CV_PATH.exists():
        return Response(status_code=503, content="CV not yet available")
    return FileResponse(
        CV_PATH,
        media_type="application/pdf",
    )


@app.websocket("/ws/arrivals/{station}/{line}")
@app.websocket("/ws/arrivals/{station}/{line}/{direction}")
async def ws_get_arrivals(
    websocket: WebSocket, station: str, line: str, direction: Direction | None = None
) -> None:
    await websocket.accept()
    logger.info("Opened connection")
    try:
        while True:
            raw_data = await get_arrivals(station, line, direction)
            data = [model.model_dump_json() for model in raw_data]
            await websocket.send_text("\n".join(data))
            await asyncio.sleep(2)
    except WebSocketDisconnect:
        logger.info("Closed connection")


@app.websocket("/ws/status/{line}")
async def ws_get_status(
    websocket: WebSocket,
    line: str,
) -> None:
    await websocket.accept()
    logger.info("Opened connection")
    try:
        while True:
            raw_data = await get_line_status(line)
            await websocket.send_text(raw_data.model_dump_json())
            await asyncio.sleep(2)
    except WebSocketDisconnect:
        logger.info("Closed connection")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.backend.main:app",
        port=BACKEND_PORT,
        reload=True,
        host="0.0.0.0",
        log_config=LOGGING_CONFIG,
    )

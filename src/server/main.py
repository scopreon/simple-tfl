import asyncio

from websockets.asyncio.server import ServerConnection, serve
from websockets.exceptions import ConnectionClosedOK

from .tfl import get_arrivals


async def echo(websocket: ServerConnection) -> None:
    async for message in websocket:
        print("Opened connection")
        try:
            while True:
                raw_data = await get_arrivals("bank", "northern")
                data = [model.model_dump_json() for model in raw_data]
                await websocket.send("\n".join(data))
                await asyncio.sleep(2)
        except ConnectionClosedOK:
            print("Closed connection")


async def main() -> None:
    async with serve(echo, "localhost", 8765) as server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())

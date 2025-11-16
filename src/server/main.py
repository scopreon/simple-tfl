import asyncio

from websockets.asyncio.server import ServerConnection, serve


async def echo(websocket: ServerConnection) -> None:
    async for message in websocket:
        while True:
            data = input("Message to send: ")
            await websocket.send(data)


async def main() -> None:
    async with serve(echo, "localhost", 8765) as server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())

import asyncio
from grpclib.client import Channel
from lib.analyzer.v1 import SendEvent


# hello
async def main() -> None:
    channel = Channel(host="127.0.0.1", port=50051)


if __name__ == "__main__":
    asyncio.run(main())

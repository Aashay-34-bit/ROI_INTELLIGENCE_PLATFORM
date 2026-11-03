import asyncio


class ConcurrencyLimiter:
    def __init__(self, limit: int = 16) -> None:
        self.semaphore = asyncio.Semaphore(limit)

    async def run(self, coro: object) -> object:
        async with self.semaphore:
            return await coro

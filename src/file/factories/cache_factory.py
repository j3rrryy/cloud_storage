import asyncio

from cashews import Cache

from settings import Settings


class CacheFactory:
    def __init__(self):
        self._cache = None

    async def initialize(self) -> None:
        try:
            await self._setup_cache()
        except Exception:
            await self.close()
            raise

    async def close(self) -> None:
        if self._cache is not None:
            try:
                await self._cache.close()
            finally:
                self._cache = None

    async def _setup_cache(self) -> None:
        self._cache = Cache()
        self._cache.setup(
            f"redis://{Settings.REDIS_USER}:{Settings.REDIS_PASSWORD}@"
            + f"{Settings.REDIS_HOST}:{Settings.REDIS_PORT}/{Settings.REDIS_DB}",
            client_side=True,
        )

    def get_cache(self) -> Cache:
        if not self._cache:
            raise RuntimeError("RedisCache not initialized")
        return self._cache

    async def is_ready(self) -> bool:
        if not self._cache:
            return False
        try:
            async with asyncio.timeout(1):
                await self._cache.ping()
            return True
        except Exception:
            return False

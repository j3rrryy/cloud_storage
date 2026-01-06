import asyncio

from cashews import Cache

from controller import AuthController
from proto import AuthServicer
from protocols import AuthRepositoryProtocol
from service import AuthService

from .auth_repository_factory import AuthRepositoryFactory
from .cache_factory import CacheFactory


class ServiceFactory:
    def __init__(self):
        self._auth_repository_factory = AuthRepositoryFactory()
        self._cache_factory = CacheFactory()
        self._auth_controller = None

    async def initialize(self) -> None:
        try:
            await asyncio.gather(
                self._auth_repository_factory.initialize(),
                self._cache_factory.initialize(),
            )
        except Exception:
            await self.close()
            raise

    async def close(self) -> None:
        await asyncio.gather(
            self._auth_repository_factory.close(),
            self._cache_factory.close(),
            return_exceptions=True,
        )

    def get_auth_repository(self) -> AuthRepositoryProtocol:
        return self._auth_repository_factory.get_auth_repository()

    def get_cache(self) -> Cache:
        return self._cache_factory.get_cache()

    def get_auth_controller(self) -> AuthServicer:
        if not self._auth_controller:
            auth_service = AuthService(self.get_auth_repository(), self.get_cache())
            self._auth_controller = AuthController(auth_service)
        return self._auth_controller

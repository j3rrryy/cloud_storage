import asyncio
from typing import Awaitable, Callable

from cashews import Cache

from controller import AuthController
from proto import AuthServicer
from protocols import AuthRepositoryProtocol, GeoIPServiceProtocol
from service import AuthService

from .auth_repository_factory import AuthRepositoryFactory
from .cache_factory import CacheFactory
from .geo_ip_service_factory import GeoIPServiceFactory


class ServiceFactory:
    def __init__(self):
        self._auth_repository_factory = AuthRepositoryFactory()
        self._cache_factory = CacheFactory()
        self._geo_ip_service_factory = GeoIPServiceFactory()
        self._auth_controller = None

    async def initialize(self) -> None:
        try:
            self._geo_ip_service_factory.initialize()
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
        self._geo_ip_service_factory.close()

    def get_auth_repository(self) -> AuthRepositoryProtocol:
        return self._auth_repository_factory.get_auth_repository()

    def get_cache(self) -> Cache:
        return self._cache_factory.get_cache()

    def get_geo_ip_service(self) -> GeoIPServiceProtocol:
        return self._geo_ip_service_factory.get_geo_ip_service()

    def get_auth_controller(self) -> AuthServicer:
        if not self._auth_controller:
            auth_service = AuthService(
                self.get_auth_repository(), self.get_cache(), self.get_geo_ip_service()
            )
            self._auth_controller = AuthController(auth_service)
        return self._auth_controller

    def get_is_ready(self) -> Callable[[], Awaitable[bool]]:
        async def is_ready() -> bool:
            try:
                (
                    repository_ready,
                    cache_ready,
                    geo_ip_service_ready,
                ) = await asyncio.gather(
                    self._auth_repository_factory.is_ready(),
                    self._cache_factory.is_ready(),
                    self._geo_ip_service_factory.is_ready(),
                )
                return repository_ready and cache_ready and geo_ip_service_ready
            except Exception:
                return False

        return is_ready

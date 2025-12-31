import asyncio

from cashews import Cache

from controller import FileController
from proto import FileServicer
from protocols import FileRepositoryProtocol, FileStorageProtocol
from service import FileService

from .cache_factory import CacheFactory
from .file_repository_factory import FileRepositoryFactory
from .file_storage_factory import FileStorageFactory


class ServiceFactory:
    def __init__(self):
        self._file_repository_factory = FileRepositoryFactory()
        self._file_storage_factory = FileStorageFactory()
        self._cache_factory = CacheFactory()
        self._file_controller = None

    async def initialize(self) -> None:
        try:
            await asyncio.gather(
                self._file_repository_factory.initialize(),
                self._file_storage_factory.initialize(),
                self._cache_factory.initialize(),
            )
        except Exception:
            await self.close()
            raise

    async def close(self) -> None:
        await asyncio.gather(
            self._file_repository_factory.close(),
            self._file_storage_factory.close(),
            self._cache_factory.close(),
            return_exceptions=True,
        )

    def get_file_repository(self) -> FileRepositoryProtocol:
        return self._file_repository_factory.get_file_repository()

    def get_file_storage(self) -> FileStorageProtocol:
        return self._file_storage_factory.get_file_storage()

    def get_cache(self) -> Cache:
        return self._cache_factory.get_cache()

    def get_file_controller(self) -> FileServicer:
        if not self._file_controller:
            file_service = FileService(
                self.get_file_repository(), self.get_file_storage(), self.get_cache()
            )
            self._file_controller = FileController(file_service)
        return self._file_controller

from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from protocols import FileRepositoryProtocol
from repository import FileRepository
from settings import Settings


class FileRepositoryFactory:
    def __init__(self):
        self._engine = None
        self._file_repository = None

    async def initialize(self) -> None:
        try:
            await self._setup_file_repository()
        except Exception:
            await self.close()
            raise

    async def close(self) -> None:
        if self._engine is not None:
            try:
                await self._engine.dispose()
            finally:
                self._engine = None
                self._file_repository = None

    async def _setup_file_repository(self) -> None:
        url = URL.create(
            Settings.POSTGRES_DRIVER,
            Settings.POSTGRES_USER,
            Settings.POSTGRES_PASSWORD,
            Settings.POSTGRES_HOST,
            Settings.POSTGRES_PORT,
            Settings.POSTGRES_DB,
        )
        self._engine = create_async_engine(
            url,
            pool_pre_ping=True,
            pool_size=20,
            max_overflow=20,
            pool_timeout=30,
            pool_recycle=1800,
        )
        sessionmaker = async_sessionmaker(
            self._engine, class_=AsyncSession, expire_on_commit=False
        )
        self._file_repository = FileRepository(sessionmaker)

    def get_file_repository(self) -> FileRepositoryProtocol:
        if not self._file_repository:
            raise RuntimeError("FileRepository not initialized")
        return self._file_repository

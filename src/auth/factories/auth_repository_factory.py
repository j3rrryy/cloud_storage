import asyncio

from sqlalchemy import text
from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from protocols import AuthRepositoryProtocol
from repository import AuthRepository
from settings import Settings


class AuthRepositoryFactory:
    def __init__(self):
        self._engine = None
        self._auth_repository = None

    async def initialize(self) -> None:
        try:
            await self._setup_auth_repository()
        except Exception:
            await self.close()
            raise

    async def close(self) -> None:
        if self._engine is not None:
            try:
                await self._engine.dispose()
            finally:
                self._engine = None
                self._auth_repository = None

    async def _setup_auth_repository(self) -> None:
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
        self._auth_repository = AuthRepository(sessionmaker)

    def get_auth_repository(self) -> AuthRepositoryProtocol:
        if not self._auth_repository:
            raise RuntimeError("AuthRepository not initialized")
        return self._auth_repository

    async def is_ready(self) -> bool:
        if not self._engine or not self._auth_repository:
            return False
        try:
            async with asyncio.timeout(1):
                async with self._engine.connect() as conn:
                    await conn.execute(text("SELECT 1"))
            return True
        except Exception:
            return False

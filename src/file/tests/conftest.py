import pytest
from cashews import Cache
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from types_aiobotocore_s3 import S3Client

from adapters import MinIOAdapter
from controller import FileController
from proto import FileServicer
from protocols import (
    FileRepositoryProtocol,
    FileServiceProtocol,
    FileStorageProtocol,
    S3ClientProtocol,
)
from repository import File, FileRepository
from service import FileService
from storage import FileStorage

from .mocks import (
    create_cache,
    create_client,
    create_file,
    create_file_repository,
    create_file_storage,
    create_session,
    create_sessionmaker,
)


@pytest.fixture
def session() -> AsyncSession:
    return create_session()


@pytest.fixture
def sessionmaker(session) -> async_sessionmaker[AsyncSession]:
    return create_sessionmaker(session)


@pytest.fixture
def client() -> S3Client:
    return create_client()


@pytest.fixture
def cache() -> Cache:
    return create_cache()


@pytest.fixture
def minio_adapter(client) -> S3ClientProtocol:
    return MinIOAdapter(client)


@pytest.fixture
def file_repository(sessionmaker) -> FileRepositoryProtocol:
    return FileRepository(sessionmaker)


@pytest.fixture
def file_storage(minio_adapter) -> FileStorageProtocol:
    return FileStorage(minio_adapter)


@pytest.fixture
def mocked_file_repository() -> FileRepositoryProtocol:
    return create_file_repository()


@pytest.fixture
def mocked_file_storage() -> FileStorageProtocol:
    return create_file_storage()


@pytest.fixture
def file_service(
    mocked_file_repository, mocked_file_storage, cache
) -> FileServiceProtocol:
    return FileService(mocked_file_repository, mocked_file_storage, cache)


@pytest.fixture
def file_controller(file_service) -> FileServicer:
    return FileController(file_service)


@pytest.fixture
def file() -> File:
    return create_file()

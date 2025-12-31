import aioboto3
from aiobotocore.config import AioConfig

from adapters import MinIOAdapter
from protocols import FileStorageProtocol
from settings import Settings
from storage import FileStorage


class FileStorageFactory:
    def __init__(self):
        self._context = None
        self._file_storage = None

    async def initialize(self) -> None:
        try:
            await self._setup_file_storage()
        except Exception:
            await self.close()
            raise

    async def close(self) -> None:
        if self._context is not None:
            try:
                await self._context.__aexit__(None, None, None)
            finally:
                self._context = None
                self._file_storage = None

    async def _setup_file_storage(self) -> None:
        session = aioboto3.Session()
        config = AioConfig(
            connect_timeout=5,
            read_timeout=10,
            max_pool_connections=30,
            retries={"max_attempts": 3, "mode": "standard"},
            s3={"addressing_style": "path"},
        )
        self._context = session.client(
            "s3",
            use_ssl=False,
            verify=False,
            endpoint_url=f"http://{Settings.MINIO_HOST}:{Settings.MINIO_PORT}",
            aws_access_key_id=Settings.MINIO_ROOT_USER,
            aws_secret_access_key=Settings.MINIO_ROOT_PASSWORD,
            config=config,
        )
        client = await self._context.__aenter__()
        minio_adapter = MinIOAdapter(client)
        self._file_storage = FileStorage(minio_adapter)

    def get_file_storage(self) -> FileStorageProtocol:
        if not self._file_storage:
            raise RuntimeError("FileStorage not initialized")
        return self._file_storage

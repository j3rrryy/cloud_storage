import asyncio

import grpc

from adapters import FileGrpcAdapter
from proto import FileStub
from protocols import FileServiceProtocol
from settings import Settings


class FileServiceFactory:
    def __init__(self):
        self._file_channel = None
        self._file_service = None

    async def initialize(self) -> None:
        try:
            await self._setup_file_service()
        except Exception:
            await self.close()
            raise

    async def close(self) -> None:
        if self._file_channel is not None:
            try:
                await self._file_channel.close()
            finally:
                self._file_channel = None
                self._file_service = None

    async def _setup_file_service(self) -> None:
        self._file_channel = grpc.aio.insecure_channel(
            Settings.FILE_SERVICE, compression=grpc.Compression.Deflate
        )
        await asyncio.wait_for(
            self._file_channel.channel_ready(),
            timeout=Settings.GRPC_CHANNEL_READY_TIMEOUT,
        )
        stub = FileStub(self._file_channel)
        self._file_service = FileGrpcAdapter(stub)

    def get_file_service(self) -> FileServiceProtocol:
        if not self._file_service:
            raise RuntimeError("FileService not initialized")
        return self._file_service

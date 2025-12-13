import asyncio

import grpc

from adapters import AuthGrpcAdapter
from proto import AuthStub
from settings import Settings


class AuthFactory:
    def __init__(self):
        self._auth_channel = None
        self._auth_service = None

    async def initialize(self) -> None:
        try:
            await self._setup_auth_service()
        except Exception:
            await self.close()
            raise

    async def close(self) -> None:
        if self._auth_channel is not None:
            try:
                await self._auth_channel.close()
            finally:
                self._auth_channel = None
                self._auth_service = None

    async def _setup_auth_service(self) -> None:
        self._auth_channel = grpc.aio.insecure_channel(
            Settings.AUTH_SERVICE, compression=grpc.Compression.Deflate
        )
        await asyncio.wait_for(
            self._auth_channel.channel_ready(),
            timeout=Settings.GRPC_CHANNEL_READY_TIMEOUT,
        )
        stub = AuthStub(self._auth_channel)
        self._auth_service = AuthGrpcAdapter(stub)

    def get_auth_service(self):
        if not self._auth_service:
            raise RuntimeError("AuthService not initialized")
        return self._auth_service

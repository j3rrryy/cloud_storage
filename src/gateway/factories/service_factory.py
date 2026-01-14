import asyncio
from typing import Awaitable, Callable

from facades import ApplicationFacade, AuthFacade, FileFacade
from protocols import (
    ApplicationFacadeProtocol,
    AuthServiceProtocol,
    FileServiceProtocol,
    MailServiceProtocol,
)

from .auth_service_factory import AuthServiceFactory
from .file_service_factory import FileServiceFactory
from .mail_service_factory import MailServiceFactory


class ServiceFactory:
    def __init__(self):
        self._auth_service_factory = AuthServiceFactory()
        self._file_service_factory = FileServiceFactory()
        self._mail_service_factory = MailServiceFactory()
        self._application_facade = None

    async def initialize(self) -> None:
        try:
            await asyncio.gather(
                self._auth_service_factory.initialize(),
                self._file_service_factory.initialize(),
                self._mail_service_factory.initialize(),
            )
        except Exception:
            await self.close()
            raise

    async def close(self) -> None:
        await asyncio.gather(
            self._auth_service_factory.close(),
            self._file_service_factory.close(),
            self._mail_service_factory.close(),
            return_exceptions=True,
        )

    def get_auth_service(self) -> AuthServiceProtocol:
        return self._auth_service_factory.get_auth_service()

    def get_file_service(self) -> FileServiceProtocol:
        return self._file_service_factory.get_file_service()

    def get_mail_service(self) -> MailServiceProtocol:
        return self._mail_service_factory.get_mail_service()

    def get_application_facade(self) -> ApplicationFacadeProtocol:
        if not self._application_facade:
            auth_facade = AuthFacade(self.get_auth_service(), self.get_mail_service())
            file_facade = FileFacade(self.get_file_service())
            self._application_facade = ApplicationFacade(auth_facade, file_facade)
        return self._application_facade

    def get_is_ready(self) -> Callable[[], Awaitable[bool]]:
        async def is_ready() -> bool:
            try:
                auth_ready, file_ready, mail_ready = await asyncio.gather(
                    self._auth_service_factory.is_ready(),
                    self._file_service_factory.is_ready(),
                    self._mail_service_factory.is_ready(),
                )
                return auth_ready and file_ready and mail_ready
            except Exception:
                return False

        return is_ready

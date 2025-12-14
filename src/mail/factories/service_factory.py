import asyncio

from facades import ApplicationFacade, AuthFacade, FileFacade
from protocols import ApplicationFacadeProtocol

from .kafka_consumer_factory import AuthFactory
from .mail_factory import MailFactory
from .smtp_client_factory import FileFactory


class ServiceFactory:
    def __init__(self):
        self._auth_factory = AuthFactory()
        self._file_factory = FileFactory()
        self._mail_factory = MailFactory()
        self._application_facade = None

    async def initialize(self) -> None:
        try:
            await asyncio.gather(
                self._auth_factory.initialize(),
                self._file_factory.initialize(),
                self._mail_factory.initialize(),
            )
        except Exception:
            await self.close()
            raise

    async def close(self) -> None:
        await asyncio.gather(
            self._auth_factory.close(),
            self._file_factory.close(),
            self._mail_factory.close(),
            return_exceptions=True,
        )

    def get_auth_service(self):
        return self._auth_factory.get_auth_service()

    def get_file_service(self):
        return self._file_factory.get_file_service()

    def get_mail_service(self):
        return self._mail_factory.get_mail_service()

    def get_application_facade(self) -> ApplicationFacadeProtocol:
        if not self._application_facade:
            auth_facade = AuthFacade(self.get_auth_service(), self.get_mail_service())
            file_facade = FileFacade(self.get_file_service())
            self._application_facade = ApplicationFacade(auth_facade, file_facade)
        return self._application_facade

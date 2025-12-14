from dto import BaseMailDTO
from protocols import SMTPClientProtocol, SMTPFacadeProtocol


class SMTPFacade(SMTPFacadeProtocol):
    def __init__(self, smtp_client: SMTPClientProtocol):
        self._smtp_client = smtp_client

    async def send_message(self, message: BaseMailDTO) -> None:
        # TODO
        await self._smtp_client.send_message()

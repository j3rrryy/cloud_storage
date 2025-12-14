from dto import BaseMailDTO
from protocols import MailStrategyProtocol, SMTPClientProtocol, SMTPFacadeProtocol
from strategies import InfoMailStrategy, ResetMailStrategy, VerificationMailStrategy


class SMTPFacade(SMTPFacadeProtocol):
    _strategies: list[MailStrategyProtocol] = [
        VerificationMailStrategy,
        InfoMailStrategy,
        ResetMailStrategy,
    ]

    def __init__(self, smtp_client: SMTPClientProtocol):
        self._smtp_client = smtp_client

    async def send_mail(self, dto: BaseMailDTO) -> None:
        for strategy in self._strategies:
            if strategy.can_construct(dto):
                mail = strategy.construct_mail(dto)
                await self._smtp_client.send_mail(mail)
                return

        raise ValueError(f"No strategy found for {dto.__class__.__name__}")

from typing import Protocol

from dto import mail_dto


class MailServiceProtocol(Protocol):
    async def verification(
        self, verification_mail: mail_dto.VerificationMailDTO
    ) -> None: ...

    async def info(self, info_mail: mail_dto.InfoMailDTO) -> None: ...

    async def reset(self, reset_mail: mail_dto.ResetMailDTO) -> None: ...

from datetime import date
from email.mime import multipart, text

from dto import InfoMailDTO, ResetMailDTO, VerificationMailDTO
from settings import Settings

from .base_template import BASE_TEMPLATE
from .info_template import INFO_CONTENT, INFO_FOOTER, INFO_HEADER
from .reset_template import RESET_CONTENT, RESET_FOOTER, RESET_HEADER
from .verification_template import (
    VERIFICATION_CONTENT,
    VERIFICATION_FOOTER,
    VERIFICATION_HEADER,
)


class MailRenderer:
    @classmethod
    def verification(cls, dto: VerificationMailDTO) -> multipart.MIMEMultipart:
        verification_url = Settings.VERIFICATION_URL + dto.verification_token
        rendered_content = VERIFICATION_CONTENT.format(
            username=dto.username, verification_url=verification_url
        )
        return cls._render(
            dto.email, VERIFICATION_HEADER, rendered_content, VERIFICATION_FOOTER
        )

    @classmethod
    def info(cls, dto: InfoMailDTO) -> multipart.MIMEMultipart:
        rendered_content = INFO_CONTENT.format(
            username=dto.username, user_ip=dto.user_ip, browser=dto.browser
        )
        return cls._render(dto.email, INFO_HEADER, rendered_content, INFO_FOOTER)

    @classmethod
    def reset(cls, dto: ResetMailDTO) -> multipart.MIMEMultipart:
        rendered_content = RESET_CONTENT.format(username=dto.username, code=dto.code)
        return cls._render(dto.email, RESET_HEADER, rendered_content, RESET_FOOTER)

    @staticmethod
    def _render(
        recipient_email: str, header: str, content: str, footer: str
    ) -> multipart.MIMEMultipart:
        mail = multipart.MIMEMultipart("alternative")
        mail["Subject"] = header
        mail["From"] = Settings.MAIL_USERNAME
        mail["To"] = recipient_email

        rendered_html = BASE_TEMPLATE.format(
            header=header,
            content=content,
            footer=footer,
            year=date.today().year,
            app_name=Settings.APP_NAME,
        )
        mail.attach(text.MIMEText(rendered_html, "html"))
        return mail

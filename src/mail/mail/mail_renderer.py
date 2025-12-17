from datetime import date
from email.mime import multipart, text

from dto import EmailConfirmationMailDTO, NewLoginMailDTO, PasswordResetMailDTO
from settings import Settings

from .base_template import BASE_TEMPLATE
from .email_confirmation_template import (
    EMAIL_CONFIRMATION_CONTENT,
    EMAIL_CONFIRMATION_FOOTER,
    EMAIL_CONFIRMATION_HEADER,
)
from .new_login_template import NEW_LOGIN_CONTENT, NEW_LOGIN_FOOTER, NEW_LOGIN_HEADER
from .password_reset_template import (
    PASSWORD_RESET_CONTENT,
    PASSWORD_RESET_FOOTER,
    PASSWORD_RESET_HEADER,
)


class MailRenderer:
    @classmethod
    def email_confirmation(
        cls, dto: EmailConfirmationMailDTO
    ) -> multipart.MIMEMultipart:
        confirmation_url = Settings.EMAIL_CONFIRMATION_URL + dto.token
        rendered_content = EMAIL_CONFIRMATION_CONTENT.format(
            username=dto.username, confirmation_url=confirmation_url
        )
        return cls._render(
            dto.email,
            EMAIL_CONFIRMATION_HEADER,
            rendered_content,
            EMAIL_CONFIRMATION_FOOTER,
        )

    @classmethod
    def new_login(cls, dto: NewLoginMailDTO) -> multipart.MIMEMultipart:
        rendered_content = NEW_LOGIN_CONTENT.format(
            username=dto.username, user_ip=dto.user_ip, browser=dto.browser
        )
        return cls._render(
            dto.email, NEW_LOGIN_HEADER, rendered_content, NEW_LOGIN_FOOTER
        )

    @classmethod
    def password_reset(cls, dto: PasswordResetMailDTO) -> multipart.MIMEMultipart:
        rendered_content = PASSWORD_RESET_CONTENT.format(
            username=dto.username, code=dto.code
        )
        return cls._render(
            dto.email, PASSWORD_RESET_HEADER, rendered_content, PASSWORD_RESET_FOOTER
        )

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

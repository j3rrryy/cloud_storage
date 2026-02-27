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
        content = cls._with_locale(EMAIL_CONFIRMATION_CONTENT, dto.locale)
        rendered_content = content.format(
            username=dto.username,
            app_name=Settings.APP_NAME,
            confirmation_url=Settings.EMAIL_CONFIRMATION_URL + dto.token,
        )
        return cls._render(
            dto.email,
            dto.locale,
            EMAIL_CONFIRMATION_HEADER,
            rendered_content,
            EMAIL_CONFIRMATION_FOOTER,
        )

    @classmethod
    def new_login(cls, dto: NewLoginMailDTO) -> multipart.MIMEMultipart:
        content = cls._with_locale(NEW_LOGIN_CONTENT, dto.locale)
        rendered_content = content.format(
            username=dto.username,
            app_name=Settings.APP_NAME,
            user_ip=dto.user_ip,
            country_code=dto.country_code,
            browser=dto.browser,
        )
        return cls._render(
            dto.email, dto.locale, NEW_LOGIN_HEADER, rendered_content, NEW_LOGIN_FOOTER
        )

    @classmethod
    def password_reset(cls, dto: PasswordResetMailDTO) -> multipart.MIMEMultipart:
        content = cls._with_locale(PASSWORD_RESET_CONTENT, dto.locale)
        rendered_content = content.format(
            username=dto.username, app_name=Settings.APP_NAME, code=dto.code
        )
        return cls._render(
            dto.email,
            dto.locale,
            PASSWORD_RESET_HEADER,
            rendered_content,
            PASSWORD_RESET_FOOTER,
        )

    @classmethod
    def _render(
        cls,
        recipient_email: str,
        locale: str,
        header: dict[str, str],
        rendered_content: str,
        footer: dict[str, str],
    ) -> multipart.MIMEMultipart:
        header_text = cls._with_locale(header, locale)
        rendered_header = header_text.format(app_name=Settings.APP_NAME)

        mail = multipart.MIMEMultipart("alternative")
        mail["Subject"] = rendered_header
        mail["From"] = Settings.MAIL_USERNAME
        mail["To"] = recipient_email

        rendered_html = BASE_TEMPLATE.format(
            header=rendered_header,
            content=rendered_content,
            footer=footer.get(locale, footer[Settings.DEFAULT_LOCALE]),
            year=date.today().year,
            app_name=Settings.APP_NAME,
        )
        mail.attach(text.MIMEText(rendered_html, "html"))
        return mail

    @staticmethod
    def _with_locale(translations: dict[str, str], locale: str) -> str:
        return translations.get(locale, translations[Settings.DEFAULT_LOCALE])

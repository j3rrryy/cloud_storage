from dto import auth_dto, mail_dto
from protocols import AuthFacadeProtocol, AuthServiceProtocol, MailServiceProtocol


class AuthFacade(AuthFacadeProtocol):
    def __init__(
        self, auth_service: AuthServiceProtocol, mail_service: MailServiceProtocol
    ):
        self._auth_service = auth_service
        self._mail_service = mail_service

    async def register(self, data: auth_dto.RegistrationDTO) -> None:
        verification_mail = await self._auth_service.register(data)
        await self._mail_service.verification(verification_mail)

    async def verify_email(self, verification_token: str) -> None:
        await self._auth_service.verify_email(verification_token)

    async def request_reset_code(self, email: str) -> str:
        reset_info = await self._auth_service.request_reset_code(email)
        reset_mail = mail_dto.ResetMailDTO(reset_info.code, reset_info.username, email)
        await self._mail_service.reset(reset_mail)
        return reset_info.user_id

    async def validate_reset_code(self, data: auth_dto.ResetCodeDTO) -> bool:
        return await self._auth_service.validate_reset_code(data)

    async def reset_password(self, data: auth_dto.ResetPasswordDTO) -> None:
        await self._auth_service.reset_password(data)

    async def log_in(self, data: auth_dto.LogInDTO) -> auth_dto.LogInDataDTO:
        login_data = await self._auth_service.log_in(data)
        if login_data.verified:
            info_mail = mail_dto.InfoMailDTO(
                data.username, login_data.email, data.user_ip, login_data.browser
            )
            await self._mail_service.info(info_mail)
        return login_data

    async def log_out(self, access_token: str) -> None:
        await self._auth_service.log_out(access_token)

    async def resend_verification_mail(self, access_token: str) -> None:
        verification_mail = await self._auth_service.resend_verification_mail(
            access_token
        )
        await self._mail_service.verification(verification_mail)

    async def auth(self, access_token: str) -> str:
        return await self._auth_service.auth(access_token)

    async def refresh(self, data: auth_dto.RefreshDTO) -> auth_dto.TokensDTO:
        return await self._auth_service.refresh(data)

    async def session_list(self, access_token: str) -> list[auth_dto.SessionDTO]:
        return await self._auth_service.session_list(access_token)

    async def revoke_session(self, data: auth_dto.RevokeSessionDTO) -> None:
        await self._auth_service.revoke_session(data)

    async def profile(self, access_token: str) -> auth_dto.ProfileDTO:
        return await self._auth_service.profile(access_token)

    async def update_email(self, data: auth_dto.UpdateEmailDTO) -> None:
        verification_mail = await self._auth_service.update_email(data)
        await self._mail_service.verification(verification_mail)

    async def update_password(self, data: auth_dto.UpdatePasswordDTO) -> None:
        await self._auth_service.update_password(data)

    async def delete_profile(self, access_token: str) -> str:
        return await self._auth_service.delete_profile(access_token)

from typing import Generator

from dto import auth_dto, mail_dto
from proto import auth_pb2 as pb2

from .base_service import RPCBaseService


class AuthService(RPCBaseService):
    @RPCBaseService.exception_handler
    async def register(
        self, data: auth_dto.RegistrationDTO
    ) -> mail_dto.VerificationMailDTO:
        request = pb2.RegisterRequest(**data.dict())
        verification_mail = await self._stub.Register(request)
        return self.convert_to_dto(verification_mail, mail_dto.VerificationMailDTO)

    @RPCBaseService.exception_handler
    async def verify_email(self, verification_token: str) -> None:
        request = pb2.VerificationToken(verification_token=verification_token)
        await self._stub.VerifyEmail(request)

    @RPCBaseService.exception_handler
    async def request_reset_code(self, email: str) -> auth_dto.ResetInfoDTO:
        request = pb2.Email(email=email)
        reset_info = await self._stub.RequestResetCode(request)
        return self.convert_to_dto(reset_info, auth_dto.ResetInfoDTO)

    @RPCBaseService.exception_handler
    async def validate_code(self, data: auth_dto.ResetCodeDTO) -> bool:
        request = pb2.ResetCodeRequest(**data.dict())
        validation_info = await self._stub.ValidateResetCode(request)
        return validation_info.is_valid

    @RPCBaseService.exception_handler
    async def reset_password(self, data: auth_dto.ResetPasswordDTO) -> None:
        request = pb2.ResetPasswordRequest(**data.dict())
        await self._stub.ResetPassword(request)

    @RPCBaseService.exception_handler
    async def log_in(self, data: auth_dto.LogInDTO) -> auth_dto.LogInDataDTO:
        request = pb2.LogInRequest(**data.dict())
        login_data = await self._stub.LogIn(request)
        return self.convert_to_dto(login_data, auth_dto.LogInDataDTO)

    @RPCBaseService.exception_handler
    async def log_out(self, access_token: str) -> None:
        request = pb2.AccessToken(access_token=access_token)
        await self._stub.LogOut(request)

    @RPCBaseService.exception_handler
    async def resend_verification_mail(
        self, access_token: str
    ) -> mail_dto.VerificationMailDTO:
        request = pb2.AccessToken(access_token=access_token)
        verification_mail = await self._stub.ResendVerificationMail(request)
        return self.convert_to_dto(verification_mail, mail_dto.VerificationMailDTO)

    @RPCBaseService.exception_handler
    async def auth(self, access_token: str) -> str:
        request = pb2.AccessToken(access_token=access_token)
        user_id = await self._stub.Auth(request)
        return user_id.user_id

    @RPCBaseService.exception_handler
    async def refresh(self, data: auth_dto.RefreshDTO) -> auth_dto.TokensDTO:
        request = pb2.RefreshRequest(**data.dict())
        tokens = await self._stub.Refresh(request)
        return self.convert_to_dto(tokens, auth_dto.TokensDTO)

    @RPCBaseService.exception_handler
    async def session_list(
        self, access_token: str
    ) -> Generator[auth_dto.SessionDTO, None, None]:
        request = pb2.AccessToken(access_token=access_token)
        sessions = await self._stub.SessionList(request)
        return (
            self.convert_to_dto(session, auth_dto.SessionDTO)
            for session in sessions.sessions
        )

    @RPCBaseService.exception_handler
    async def revoke_session(self, data: auth_dto.RevokeSessionDTO) -> None:
        request = pb2.RevokeSessionRequest(**data.dict())
        await self._stub.RevokeSession(request)

    @RPCBaseService.exception_handler
    async def profile(self, access_token: str) -> auth_dto.ProfileDTO:
        request = pb2.AccessToken(access_token=access_token)
        user_profile = await self._stub.Profile(request)
        return self.convert_to_dto(user_profile, auth_dto.ProfileDTO)

    @RPCBaseService.exception_handler
    async def update_email(
        self, data: auth_dto.UpdateEmailDTO
    ) -> mail_dto.VerificationMailDTO:
        request = pb2.UpdateEmailRequest(**data.dict())
        verification_mail = await self._stub.UpdateEmail(request)
        return self.convert_to_dto(verification_mail, mail_dto.VerificationMailDTO)

    @RPCBaseService.exception_handler
    async def update_password(self, data: auth_dto.UpdatePasswordDTO) -> None:
        request = pb2.UpdatePasswordRequest(**data.dict())
        await self._stub.UpdatePassword(request)

    @RPCBaseService.exception_handler
    async def delete_profile(self, access_token: str) -> str:
        request = pb2.AccessToken(access_token=access_token)
        user_id = await self._stub.DeleteProfile(request)
        return user_id.user_id

from dto import auth_dto, mail_dto
from proto import auth_pb2 as pb2

from .base_service import RPCBaseService


class AuthService(RPCBaseService):
    @RPCBaseService.exception_handler
    async def register(
        self, data: auth_dto.RegistrationDTO
    ) -> mail_dto.VerificationMailDTO:
        request = data.to_request(pb2.RegisterRequest)
        verification_token: pb2.VerificationToken = await self._stub.Register(request)
        return mail_dto.VerificationMailDTO(
            verification_token.verification_token, data.username, data.email
        )

    @RPCBaseService.exception_handler
    async def verify_email(self, verification_token: str) -> None:
        request = pb2.VerificationToken(verification_token=verification_token)
        await self._stub.VerifyEmail(request)

    @RPCBaseService.exception_handler
    async def request_reset_code(self, email: str) -> auth_dto.ResetInfoDTO:
        request = pb2.Email(email=email)
        reset_info: pb2.ResetCodeResponse = await self._stub.RequestResetCode(request)
        return auth_dto.ResetInfoDTO.from_response(reset_info)

    @RPCBaseService.exception_handler
    async def validate_code(self, data: auth_dto.ResetCodeDTO) -> bool:
        request = data.to_request(pb2.ResetCodeRequest)
        validation_info: pb2.CodeIsValid = await self._stub.ValidateResetCode(request)
        return validation_info.is_valid

    @RPCBaseService.exception_handler
    async def reset_password(self, data: auth_dto.ResetPasswordDTO) -> None:
        request = data.to_request(pb2.ResetPasswordRequest)
        await self._stub.ResetPassword(request)

    @RPCBaseService.exception_handler
    async def log_in(self, data: auth_dto.LogInDTO) -> auth_dto.LogInDataDTO:
        request = data.to_request(pb2.LogInRequest)
        login_data: pb2.LogInResponse = await self._stub.LogIn(request)
        return auth_dto.LogInDataDTO.from_response(login_data)

    @RPCBaseService.exception_handler
    async def log_out(self, access_token: str) -> None:
        request = pb2.AccessToken(access_token=access_token)
        await self._stub.LogOut(request)

    @RPCBaseService.exception_handler
    async def resend_verification_mail(
        self, access_token: str
    ) -> mail_dto.VerificationMailDTO:
        request = pb2.AccessToken(access_token=access_token)
        verification_mail: pb2.VerificationMail = (
            await self._stub.ResendVerificationMail(request)
        )
        return mail_dto.VerificationMailDTO.from_response(verification_mail)

    @RPCBaseService.exception_handler
    async def auth(self, access_token: str) -> str:
        request = pb2.AccessToken(access_token=access_token)
        user_id: pb2.UserId = await self._stub.Auth(request)
        return user_id.user_id

    @RPCBaseService.exception_handler
    async def refresh(self, data: auth_dto.RefreshDTO) -> auth_dto.TokensDTO:
        request = data.to_request(pb2.RefreshRequest)
        tokens: pb2.Tokens = await self._stub.Refresh(request)
        return auth_dto.TokensDTO.from_response(tokens)

    @RPCBaseService.exception_handler
    async def session_list(self, access_token: str) -> list[auth_dto.SessionDTO]:
        request = pb2.AccessToken(access_token=access_token)
        sessions: pb2.Sessions = await self._stub.SessionList(request)
        return [
            auth_dto.SessionDTO.from_response(session) for session in sessions.sessions
        ]

    @RPCBaseService.exception_handler
    async def revoke_session(self, data: auth_dto.RevokeSessionDTO) -> None:
        request = data.to_request(pb2.RevokeSessionRequest)
        await self._stub.RevokeSession(request)

    @RPCBaseService.exception_handler
    async def profile(self, access_token: str) -> auth_dto.ProfileDTO:
        request = pb2.AccessToken(access_token=access_token)
        user_profile: pb2.ProfileResponse = await self._stub.Profile(request)
        return auth_dto.ProfileDTO.from_response(user_profile)

    @RPCBaseService.exception_handler
    async def update_email(
        self, data: auth_dto.UpdateEmailDTO
    ) -> mail_dto.VerificationMailDTO:
        request = data.to_request(pb2.UpdateEmailRequest)
        verification_mail: pb2.VerificationMail = await self._stub.UpdateEmail(request)
        return mail_dto.VerificationMailDTO.from_response(verification_mail)

    @RPCBaseService.exception_handler
    async def update_password(self, data: auth_dto.UpdatePasswordDTO) -> None:
        request = data.to_request(pb2.UpdatePasswordRequest)
        await self._stub.UpdatePassword(request)

    @RPCBaseService.exception_handler
    async def delete_profile(self, access_token: str) -> str:
        request = pb2.AccessToken(access_token=access_token)
        user_id: pb2.UserId = await self._stub.DeleteProfile(request)
        return user_id.user_id

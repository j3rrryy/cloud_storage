from google.protobuf import empty_pb2

from dto import request as request_dto
from proto import AuthServicer
from proto import auth_pb2 as pb2
from protocols import AuthServiceProtocol


class AuthController(AuthServicer):
    def __init__(self, auth_service: AuthServiceProtocol):
        self._auth_service = auth_service

    async def Register(self, request, context):
        dto = request_dto.RegisterRequestDTO.from_request(request)
        token = await self._auth_service.register(dto)
        return pb2.Token(token=token)

    async def ConfirmEmail(self, request, context):
        await self._auth_service.confirm_email(request.token)
        return empty_pb2.Empty()

    async def RequestResetCode(self, request, context):
        reset_mail = await self._auth_service.request_reset_code(request.email)
        return reset_mail.to_response(pb2.ResetCodeResponse)

    async def ValidateResetCode(self, request, context):
        dto = request_dto.ResetCodeRequestDTO.from_request(request)
        is_valid = await self._auth_service.validate_reset_code(dto)
        return pb2.CodeIsValid(is_valid=is_valid)

    async def ResetPassword(self, request, context):
        dto = request_dto.ResetPasswordRequestDTO.from_request(request)
        await self._auth_service.reset_password(dto)
        return empty_pb2.Empty()

    async def LogIn(self, request, context):
        dto = request_dto.LogInRequestDTO.from_request(request)
        login_data = await self._auth_service.log_in(dto)
        return login_data.to_response(pb2.LogInResponse)

    async def LogOut(self, request, context):
        await self._auth_service.log_out(request.access_token)
        return empty_pb2.Empty()

    async def ResendEmailConfirmationMail(self, request, context):
        email_confirmation_mail = (
            await self._auth_service.resend_email_confirmation_mail(
                request.access_token
            )
        )
        return email_confirmation_mail.to_response(pb2.EmailConfirmationMail)

    async def Auth(self, request, context):
        user_id = await self._auth_service.auth(request.access_token)
        return pb2.UserId(user_id=user_id)

    async def Refresh(self, request, context):
        dto = request_dto.RefreshRequestDTO.from_request(request)
        tokens = await self._auth_service.refresh(dto)
        return tokens.to_response(pb2.Tokens)

    async def SessionList(self, request, context):
        sessions = await self._auth_service.session_list(request.access_token)
        return pb2.Sessions(
            sessions=(session.to_response(pb2.SessionInfo) for session in sessions)
        )

    async def RevokeSession(self, request, context):
        dto = request_dto.RevokeSessionRequestDTO.from_request(request)
        await self._auth_service.revoke_session(dto)
        return empty_pb2.Empty()

    async def Profile(self, request, context):
        profile = await self._auth_service.profile(request.access_token)
        return profile.to_response(pb2.ProfileResponse)

    async def UpdateEmail(self, request, context):
        dto = request_dto.UpdateEmailRequestDTO.from_request(request)
        email_confirmation_mail = await self._auth_service.update_email(dto)
        return email_confirmation_mail.to_response(pb2.EmailConfirmationMail)

    async def UpdatePassword(self, request, context):
        dto = request_dto.UpdatePasswordRequestDTO.from_request(request)
        await self._auth_service.update_password(dto)
        return empty_pb2.Empty()

    async def DeleteProfile(self, request, context):
        user_id = await self._auth_service.delete_profile(request.access_token)
        return pb2.UserId(user_id=user_id)

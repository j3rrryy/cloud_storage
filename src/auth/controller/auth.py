from google.protobuf import empty_pb2

from config import load_config
from dto import request as request_dto
from proto import AuthServicer
from proto import auth_pb2 as pb2
from service import AuthService
from utils import ExceptionHandler


class AuthController(AuthServicer):
    _eh = ExceptionHandler(load_config().app.logger)

    async def Register(self, request, context):
        dto = request_dto.RegisterRequestDTO.from_request(request)
        verification_mail = await self._eh(context, AuthService.register, dto)
        return pb2.VerificationMail(**verification_mail.dict())

    async def VerifyEmail(self, request, context):
        await self._eh(context, AuthService.verify_email, request.verification_token)
        return empty_pb2.Empty()

    async def RequestResetCode(self, request, context):
        reset_mail = await self._eh(
            context, AuthService.request_reset_code, request.email
        )
        return pb2.ResetCodeResponse(**reset_mail.dict())

    async def ValidateResetCode(self, request, context):
        dto = request_dto.ResetCodeRequestDTO.from_request(request)
        is_valid = await self._eh(context, AuthService.validate_reset_code, dto)
        return pb2.CodeIsValid(is_valid=is_valid)

    async def ResetPassword(self, request, context):
        dto = request_dto.ResetPasswordRequestDTO.from_request(request)
        await self._eh(context, AuthService.reset_password, dto)
        return empty_pb2.Empty()

    async def LogIn(self, request, context):
        dto = request_dto.LogInRequestDTO.from_request(request)
        login_data = await self._eh(context, AuthService.log_in, dto)
        return pb2.LogInResponse(**login_data.dict())

    async def LogOut(self, request, context):
        await self._eh(context, AuthService.log_out, request.access_token)
        return empty_pb2.Empty()

    async def ResendVerificationMail(self, request, context):
        verification_mail = await self._eh(
            context, AuthService.resend_verification_mail, request.access_token
        )
        return pb2.VerificationMail(**verification_mail.dict())

    async def Auth(self, request, context):
        user_id = await self._eh(context, AuthService.auth, request.access_token)
        return pb2.UserId(user_id=user_id)

    async def Refresh(self, request, context):
        dto = request_dto.RefreshRequestDTO.from_request(request)
        tokens = await self._eh(context, AuthService.refresh, dto)
        return pb2.Tokens(**tokens.dict())

    async def SessionList(self, request, context):
        sessions = await self._eh(
            context, AuthService.session_list, request.access_token
        )
        return pb2.Sessions(
            sessions=(pb2.SessionInfo(**session.dict()) for session in sessions)
        )

    async def RevokeSession(self, request, context):
        dto = request_dto.RevokeSessionRequestDTO.from_request(request)
        await self._eh(context, AuthService.revoke_session, dto)
        return empty_pb2.Empty()

    async def Profile(self, request, context):
        profile = await self._eh(context, AuthService.profile, request.access_token)
        return pb2.ProfileResponse(**profile.dict())

    async def UpdateEmail(self, request, context):
        dto = request_dto.UpdateEmailRequestDTO.from_request(request)
        verification_mail = await self._eh(context, AuthService.update_email, dto)
        return pb2.VerificationMail(**verification_mail.dict())

    async def UpdatePassword(self, request, context):
        dto = request_dto.UpdatePasswordRequestDTO.from_request(request)
        await self._eh(context, AuthService.update_password, dto)
        return empty_pb2.Empty()

    async def DeleteProfile(self, request, context):
        user_id = await self._eh(
            context, AuthService.delete_profile, request.access_token
        )
        return pb2.UserId(user_id=user_id)

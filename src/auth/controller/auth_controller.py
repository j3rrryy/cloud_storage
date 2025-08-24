from google.protobuf import empty_pb2

from dto import request as request_dto
from proto import AuthServicer
from proto import auth_pb2 as pb2
from service import AuthService
from utils import ExceptionHandler


class AuthController(AuthServicer):
    async def Register(self, request, context):
        dto = request_dto.RegisterRequestDTO.from_request(request)
        verification_token = await ExceptionHandler.handle(
            context, AuthService.register, dto
        )
        return pb2.VerificationToken(verification_token=verification_token)

    async def VerifyEmail(self, request, context):
        await ExceptionHandler.handle(
            context, AuthService.verify_email, request.verification_token
        )
        return empty_pb2.Empty()

    async def RequestResetCode(self, request, context):
        reset_mail = await ExceptionHandler.handle(
            context, AuthService.request_reset_code, request.email
        )
        return pb2.ResetCodeResponse(
            user_id=reset_mail.user_id,
            username=reset_mail.username,
            code=reset_mail.code,
        )

    async def ValidateResetCode(self, request, context):
        dto = request_dto.ResetCodeRequestDTO.from_request(request)
        is_valid = await ExceptionHandler.handle(
            context, AuthService.validate_reset_code, dto
        )
        return pb2.CodeIsValid(is_valid=is_valid)

    async def ResetPassword(self, request, context):
        dto = request_dto.ResetPasswordRequestDTO.from_request(request)
        await ExceptionHandler.handle(context, AuthService.reset_password, dto)
        return empty_pb2.Empty()

    async def LogIn(self, request, context):
        dto = request_dto.LogInRequestDTO.from_request(request)
        login_data = await ExceptionHandler.handle(context, AuthService.log_in, dto)
        return pb2.LogInResponse(
            access_token=login_data.access_token,
            refresh_token=login_data.refresh_token,
            email=login_data.email,
            browser=login_data.browser,
            verified=login_data.verified,
        )

    async def LogOut(self, request, context):
        await ExceptionHandler.handle(
            context, AuthService.log_out, request.access_token
        )
        return empty_pb2.Empty()

    async def ResendVerificationMail(self, request, context):
        verification_mail = await ExceptionHandler.handle(
            context, AuthService.resend_verification_mail, request.access_token
        )
        return pb2.VerificationMail(
            verification_token=verification_mail.verification_token,
            username=verification_mail.username,
            email=verification_mail.email,
        )

    async def Auth(self, request, context):
        user_id = await ExceptionHandler.handle(
            context, AuthService.auth, request.access_token
        )
        return pb2.UserId(user_id=user_id)

    async def Refresh(self, request, context):
        dto = request_dto.RefreshRequestDTO.from_request(request)
        tokens = await ExceptionHandler.handle(context, AuthService.refresh, dto)
        return pb2.Tokens(
            access_token=tokens.access_token, refresh_token=tokens.refresh_token
        )

    async def SessionList(self, request, context):
        sessions = await ExceptionHandler.handle(
            context, AuthService.session_list, request.access_token
        )
        return pb2.Sessions(
            sessions=(
                pb2.SessionInfo(
                    session_id=session.session_id,
                    user_ip=session.user_ip,
                    browser=session.browser,
                    created_at=session.created_at,
                )
                for session in sessions
            )
        )

    async def RevokeSession(self, request, context):
        dto = request_dto.RevokeSessionRequestDTO.from_request(request)
        await ExceptionHandler.handle(context, AuthService.revoke_session, dto)
        return empty_pb2.Empty()

    async def Profile(self, request, context):
        profile = await ExceptionHandler.handle(
            context, AuthService.profile, request.access_token
        )
        return pb2.ProfileResponse(
            user_id=profile.user_id,
            username=profile.username,
            email=profile.email,
            verified=profile.verified,
            registered_at=profile.registered_at,
        )

    async def UpdateEmail(self, request, context):
        dto = request_dto.UpdateEmailRequestDTO.from_request(request)
        verification_mail = await ExceptionHandler.handle(
            context, AuthService.update_email, dto
        )
        return pb2.VerificationMail(
            verification_token=verification_mail.verification_token,
            username=verification_mail.username,
            email=verification_mail.email,
        )

    async def UpdatePassword(self, request, context):
        dto = request_dto.UpdatePasswordRequestDTO.from_request(request)
        await ExceptionHandler.handle(context, AuthService.update_password, dto)
        return empty_pb2.Empty()

    async def DeleteProfile(self, request, context):
        user_id = await ExceptionHandler.handle(
            context, AuthService.delete_profile, request.access_token
        )
        return pb2.UserId(user_id=user_id)

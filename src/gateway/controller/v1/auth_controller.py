from typing import Annotated

from litestar import Controller, MediaType, Request, Router, delete, get, patch, post
from litestar.enums import RequestEncodingType
from litestar.params import Body

from dto import auth_dto, mail_dto
from schemas import auth_schemas
from service.v1 import AuthService, FileService, MailService
from utils import validate_access_token


class AuthController(Controller):
    path = "/auth"

    @post("/register", status_code=201)
    async def register(
        self,
        data: Annotated[
            auth_schemas.Registration, Body(media_type=RequestEncodingType.MESSAGEPACK)
        ],
        auth_service_v1: AuthService,
        mail_service_v1: MailService,
    ) -> None:
        dto = auth_dto.RegistrationDTO.from_schema(data)
        verification_mail = await auth_service_v1.register(dto)
        await mail_service_v1.verification(verification_mail)

    @get("/verify-email", status_code=204)
    async def verify_email(
        self, verification_token: str, auth_service_v1: AuthService
    ) -> None:
        await auth_service_v1.verify_email(verification_token)

    @post(
        "/request-reset-code",
        status_code=200,
        response_model=auth_schemas.UserId,
        media_type=MediaType.MESSAGEPACK,
    )
    async def request_reset_code(
        self,
        data: Annotated[
            auth_schemas.ForgotPassword,
            Body(media_type=RequestEncodingType.MESSAGEPACK),
        ],
        auth_service_v1: AuthService,
        mail_service_v1: MailService,
    ) -> auth_schemas.UserId:
        reset_info = await auth_service_v1.request_reset_code(data.email)
        dto = mail_dto.ResetMailDTO(reset_info.code, reset_info.username, data.email)
        await mail_service_v1.reset(dto)
        return auth_schemas.UserId(reset_info.user_id)

    @post(
        "/validate-reset-code",
        status_code=200,
        response_model=auth_schemas.CodeIsValid,
        media_type=MediaType.MESSAGEPACK,
    )
    async def validate_reset_code(
        self,
        data: Annotated[
            auth_schemas.ResetCode, Body(media_type=RequestEncodingType.MESSAGEPACK)
        ],
        auth_service_v1: AuthService,
    ) -> auth_schemas.CodeIsValid:
        dto = auth_dto.ResetCodeDTO.from_schema(data)
        is_valid = await auth_service_v1.validate_code(dto)
        return auth_schemas.CodeIsValid(is_valid)

    @post("/reset-password", status_code=204)
    async def reset_password(
        self,
        data: Annotated[
            auth_schemas.ResetPassword, Body(media_type=RequestEncodingType.MESSAGEPACK)
        ],
        auth_service_v1: AuthService,
    ) -> None:
        dto = auth_dto.ResetPasswordDTO.from_schema(data)
        await auth_service_v1.reset_password(dto)

    @post(
        "/log-in",
        status_code=200,
        response_model=auth_schemas.Tokens,
        media_type=MediaType.MESSAGEPACK,
    )
    async def log_in(
        self,
        data: Annotated[
            auth_schemas.LogIn, Body(media_type=RequestEncodingType.MESSAGEPACK)
        ],
        request: Request,
        auth_service_v1: AuthService,
        mail_service_v1: MailService,
    ) -> auth_schemas.Tokens:
        dto = auth_dto.LogInDTO(
            data.username,
            data.password,
            request.headers.get("X-Forwarded-For", "Unknown").split(", ")[0],
            request.headers.get("User-Agent", "Unknown"),
        )
        login_data = await auth_service_v1.log_in(dto)

        if login_data.verified:  # pragma: no cover
            info_mail = mail_dto.InfoMailDTO(
                data.username, login_data.email, dto.user_ip, login_data.browser
            )
            await mail_service_v1.info(info_mail)

        return login_data.to_schema(auth_schemas.Tokens)

    @post("/log-out", status_code=204)
    async def log_out(self, request: Request, auth_service_v1: AuthService) -> None:
        access_token = validate_access_token(request)
        await auth_service_v1.log_out(access_token)

    @post("/resend-verification-mail", status_code=204)
    async def resend_verification_mail(
        self,
        request: Request,
        auth_service_v1: AuthService,
        mail_service_v1: MailService,
    ) -> None:
        access_token = validate_access_token(request)
        verification_mail = await auth_service_v1.resend_verification_mail(access_token)
        await mail_service_v1.verification(verification_mail)

    @get(
        "/auth",
        status_code=200,
        response_model=auth_schemas.UserId,
        media_type=MediaType.MESSAGEPACK,
    )
    async def auth_user(
        self, request: Request, auth_service_v1: AuthService
    ) -> auth_schemas.UserId:
        access_token = validate_access_token(request)
        user_id = await auth_service_v1.auth(access_token)
        return auth_schemas.UserId(user_id)

    @post(
        "/refresh",
        status_code=201,
        response_model=auth_schemas.Tokens,
        media_type=MediaType.MESSAGEPACK,
    )
    async def refresh(
        self,
        data: Annotated[
            auth_schemas.RefreshToken, Body(media_type=RequestEncodingType.MESSAGEPACK)
        ],
        request: Request,
        auth_service_v1: AuthService,
    ) -> auth_schemas.Tokens:
        dto = auth_dto.RefreshDTO(
            data.refresh_token,
            request.headers.get("X-Forwarded-For", "Unknown").split(", ")[0],
            request.headers.get("User-Agent", "Unknown"),
        )
        tokens = await auth_service_v1.refresh(dto)
        return tokens.to_schema(auth_schemas.Tokens)

    @get(
        "/session-list",
        status_code=200,
        response_model=auth_schemas.SessionList,
        media_type=MediaType.MESSAGEPACK,
    )
    async def session_list(
        self, request: Request, auth_service_v1: AuthService
    ) -> auth_schemas.SessionList:
        access_token = validate_access_token(request)
        sessions = await auth_service_v1.session_list(access_token)
        return auth_schemas.SessionList(
            tuple(session.to_schema(auth_schemas.SessionInfo) for session in sessions)
        )

    @post("/revoke-session", status_code=204)
    async def revoke_session(
        self,
        data: Annotated[
            auth_schemas.SessionId, Body(media_type=RequestEncodingType.MESSAGEPACK)
        ],
        request: Request,
        auth_service_v1: AuthService,
    ) -> None:
        dto = auth_dto.RevokeSessionDTO(validate_access_token(request), data.session_id)
        await auth_service_v1.revoke_session(dto)

    @get(
        "/profile",
        status_code=200,
        response_model=auth_schemas.Profile,
        media_type=MediaType.MESSAGEPACK,
    )
    async def profile(
        self, request: Request, auth_service_v1: AuthService
    ) -> auth_schemas.Profile:
        access_token = validate_access_token(request)
        user_profile = await auth_service_v1.profile(access_token)
        return user_profile.to_schema(auth_schemas.Profile)

    @patch("/update-email", status_code=204)
    async def update_email(
        self,
        data: Annotated[
            auth_schemas.UpdateEmail, Body(media_type=RequestEncodingType.MESSAGEPACK)
        ],
        request: Request,
        auth_service_v1: AuthService,
        mail_service_v1: MailService,
    ) -> None:
        dto = auth_dto.UpdateEmailDTO(validate_access_token(request), data.new_email)
        verification_mail = await auth_service_v1.update_email(dto)
        await mail_service_v1.verification(verification_mail)

    @patch("/update-password", status_code=204)
    async def update_password(
        self,
        data: Annotated[
            auth_schemas.UpdatePassword,
            Body(media_type=RequestEncodingType.MESSAGEPACK),
        ],
        request: Request,
        auth_service_v1: AuthService,
    ) -> None:
        dto = auth_dto.UpdatePasswordDTO(
            validate_access_token(request), data.old_password, data.new_password
        )
        await auth_service_v1.update_password(dto)

    @delete("/delete-profile", status_code=204)
    async def delete_profile(
        self,
        request: Request,
        auth_service_v1: AuthService,
        file_service_v1: FileService,
    ) -> None:
        access_token = validate_access_token(request)
        user_id = await auth_service_v1.delete_profile(access_token)
        await file_service_v1.delete_all(user_id)


auth_router = Router("/v1", route_handlers=(AuthController,), tags=("auth",))

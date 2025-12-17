from typing import Annotated
from uuid import UUID

from litestar import Controller, MediaType, Request, Router, delete, get, patch, post
from litestar.enums import RequestEncodingType
from litestar.params import Body
from litestar.status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT

from dto import auth_dto
from protocols import ApplicationFacadeProtocol
from schemas import auth_schemas
from validators import validate_access_token


class AuthController(Controller):
    path = "/auth"

    @post("/register", status_code=HTTP_201_CREATED)
    async def register(
        self,
        data: Annotated[
            auth_schemas.Registration, Body(media_type=RequestEncodingType.MESSAGEPACK)
        ],
        application_facade: ApplicationFacadeProtocol,
    ) -> None:
        dto = auth_dto.RegistrationDTO.from_schema(data)
        await application_facade.register(dto)

    @get("/confirm-email", status_code=HTTP_204_NO_CONTENT)
    async def confirm_email(
        self, token: str, application_facade: ApplicationFacadeProtocol
    ) -> None:
        await application_facade.confirm_email(token)

    @post(
        "/reset-code/request",
        status_code=HTTP_200_OK,
        response_model=auth_schemas.UserId,
        media_type=MediaType.MESSAGEPACK,
    )
    async def request_reset_code(
        self,
        data: Annotated[
            auth_schemas.ForgotPassword,
            Body(media_type=RequestEncodingType.MESSAGEPACK),
        ],
        application_facade: ApplicationFacadeProtocol,
    ) -> auth_schemas.UserId:
        user_id = await application_facade.request_reset_code(data.email)
        return auth_schemas.UserId(user_id)

    @post(
        "/reset-code/validate",
        status_code=HTTP_200_OK,
        response_model=auth_schemas.CodeIsValid,
        media_type=MediaType.MESSAGEPACK,
    )
    async def validate_reset_code(
        self,
        data: Annotated[
            auth_schemas.ResetCode, Body(media_type=RequestEncodingType.MESSAGEPACK)
        ],
        application_facade: ApplicationFacadeProtocol,
    ) -> auth_schemas.CodeIsValid:
        dto = auth_dto.ResetCodeDTO.from_schema(data)
        is_valid = await application_facade.validate_reset_code(dto)
        return auth_schemas.CodeIsValid(is_valid)

    @post("/reset-password", status_code=HTTP_204_NO_CONTENT)
    async def reset_password(
        self,
        data: Annotated[
            auth_schemas.ResetPassword, Body(media_type=RequestEncodingType.MESSAGEPACK)
        ],
        application_facade: ApplicationFacadeProtocol,
    ) -> None:
        dto = auth_dto.ResetPasswordDTO.from_schema(data)
        await application_facade.reset_password(dto)

    @post(
        "/log-in",
        status_code=HTTP_200_OK,
        response_model=auth_schemas.Tokens,
        media_type=MediaType.MESSAGEPACK,
    )
    async def log_in(
        self,
        data: Annotated[
            auth_schemas.LogIn, Body(media_type=RequestEncodingType.MESSAGEPACK)
        ],
        request: Request,
        application_facade: ApplicationFacadeProtocol,
    ) -> auth_schemas.Tokens:
        dto = auth_dto.LogInDTO(
            data.username,
            data.password,
            request.headers.get("X-Forwarded-For", "Unknown").split(", ")[0],
            request.headers.get("User-Agent", "Unknown"),
        )
        login_data = await application_facade.log_in(dto)
        return login_data.to_schema(auth_schemas.Tokens)

    @post("/log-out", status_code=HTTP_204_NO_CONTENT)
    async def log_out(
        self, request: Request, application_facade: ApplicationFacadeProtocol
    ) -> None:
        access_token = validate_access_token(request)
        await application_facade.log_out(access_token)

    @post("/resend-email-confirmation-mail", status_code=HTTP_204_NO_CONTENT)
    async def resend_email_confirmation_mail(
        self, request: Request, application_facade: ApplicationFacadeProtocol
    ) -> None:
        access_token = validate_access_token(request)
        await application_facade.resend_email_confirmation_mail(access_token)

    @get(
        "/",
        status_code=HTTP_200_OK,
        response_model=auth_schemas.UserId,
        media_type=MediaType.MESSAGEPACK,
    )
    async def auth(
        self, request: Request, application_facade: ApplicationFacadeProtocol
    ) -> auth_schemas.UserId:
        access_token = validate_access_token(request)
        user_id = await application_facade.auth(access_token)
        return auth_schemas.UserId(user_id)

    @post(
        "/refresh-tokens",
        status_code=HTTP_201_CREATED,
        response_model=auth_schemas.Tokens,
        media_type=MediaType.MESSAGEPACK,
    )
    async def refresh(
        self,
        data: Annotated[
            auth_schemas.RefreshToken, Body(media_type=RequestEncodingType.MESSAGEPACK)
        ],
        request: Request,
        application_facade: ApplicationFacadeProtocol,
    ) -> auth_schemas.Tokens:
        dto = auth_dto.RefreshDTO(
            data.refresh_token,
            request.headers.get("X-Forwarded-For", "Unknown").split(", ")[0],
            request.headers.get("User-Agent", "Unknown"),
        )
        tokens = await application_facade.refresh(dto)
        return tokens.to_schema(auth_schemas.Tokens)

    @get(
        "/sessions",
        status_code=HTTP_200_OK,
        response_model=auth_schemas.SessionList,
        media_type=MediaType.MESSAGEPACK,
    )
    async def session_list(
        self, request: Request, application_facade: ApplicationFacadeProtocol
    ) -> auth_schemas.SessionList:
        access_token = validate_access_token(request)
        sessions = await application_facade.session_list(access_token)
        return auth_schemas.SessionList(
            [session.to_schema(auth_schemas.SessionInfo) for session in sessions]
        )

    @delete("/sessions/{session_id: uuid}", status_code=HTTP_204_NO_CONTENT)
    async def revoke_session(
        self,
        session_id: UUID,
        request: Request,
        application_facade: ApplicationFacadeProtocol,
    ) -> None:
        access_token = validate_access_token(request)
        dto = auth_dto.RevokeSessionDTO(access_token, str(session_id))
        await application_facade.revoke_session(dto)

    @get(
        "/profile",
        status_code=HTTP_200_OK,
        response_model=auth_schemas.Profile,
        media_type=MediaType.MESSAGEPACK,
    )
    async def profile(
        self, request: Request, application_facade: ApplicationFacadeProtocol
    ) -> auth_schemas.Profile:
        access_token = validate_access_token(request)
        user_profile = await application_facade.profile(access_token)
        return user_profile.to_schema(auth_schemas.Profile)

    @patch("/profile/email", status_code=HTTP_204_NO_CONTENT)
    async def update_email(
        self,
        data: Annotated[
            auth_schemas.UpdateEmail, Body(media_type=RequestEncodingType.MESSAGEPACK)
        ],
        request: Request,
        application_facade: ApplicationFacadeProtocol,
    ) -> None:
        access_token = validate_access_token(request)
        dto = auth_dto.UpdateEmailDTO(access_token, data.new_email)
        await application_facade.update_email(dto)

    @patch("/profile/password", status_code=HTTP_204_NO_CONTENT)
    async def update_password(
        self,
        data: Annotated[
            auth_schemas.UpdatePassword,
            Body(media_type=RequestEncodingType.MESSAGEPACK),
        ],
        request: Request,
        application_facade: ApplicationFacadeProtocol,
    ) -> None:
        access_token = validate_access_token(request)
        dto = auth_dto.UpdatePasswordDTO(
            access_token, data.old_password, data.new_password
        )
        await application_facade.update_password(dto)

    @delete("/profile", status_code=HTTP_204_NO_CONTENT)
    async def delete_profile(
        self, request: Request, application_facade: ApplicationFacadeProtocol
    ) -> None:
        access_token = validate_access_token(request)
        await application_facade.delete_profile(access_token)


auth_router = Router("/v1", route_handlers=(AuthController,), tags=("auth",))

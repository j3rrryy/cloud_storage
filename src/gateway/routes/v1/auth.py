from typing import Annotated
from uuid import UUID

from litestar import Controller, MediaType, Request, Router, delete, get, patch, post
from litestar.enums import RequestEncodingType
from litestar.params import Body

from schemas import auth
from services import Auth, Files, Mail
from utils import validate_access_token


class AuthController(Controller):
    path = "/auth"

    @post("/register", status_code=201)
    async def register(
        self,
        data: Annotated[
            auth.Registration, Body(media_type=RequestEncodingType.MESSAGEPACK)
        ],
        auth_service: Auth,
        mail_service: Mail,
    ) -> None:
        verification_mail = await auth_service.register(data.to_dict())
        await mail_service.register(verification_mail)

    @get("/verify-email", status_code=204)
    async def verify_email(self, verification_token: str, auth_service: Auth) -> None:
        await auth_service.verify_email(verification_token)

    @post(
        "/request-reset-code",
        status_code=200,
        response_model=auth.UserId,
        media_type=MediaType.MESSAGEPACK,
    )
    async def request_reset_code(
        self,
        data: Annotated[
            auth.ForgotPassword, Body(media_type=RequestEncodingType.MESSAGEPACK)
        ],
        auth_service: Auth,
        mail_service: Mail,
    ) -> auth.UserId:
        reset_code = await auth_service.request_reset_code(data.email)
        reset_code["email"] = data.email
        user_id = reset_code["user_id"]
        del reset_code["user_id"]
        await mail_service.request_reset_code(reset_code)
        return auth.UserId(UUID(user_id))

    @post(
        "/validate-reset-code",
        status_code=200,
        response_model=auth.CodeIsValid,
        media_type=MediaType.MESSAGEPACK,
    )
    async def validate_reset_code(
        self,
        data: Annotated[
            auth.ResetCode, Body(media_type=RequestEncodingType.MESSAGEPACK)
        ],
        auth_service: Auth,
    ) -> auth.CodeIsValid:
        is_valid = await auth_service.validate_code(data.to_dict())
        return auth.CodeIsValid(is_valid)

    @post("/reset-password", status_code=204)
    async def reset_password(
        self,
        data: Annotated[
            auth.ResetPassword, Body(media_type=RequestEncodingType.MESSAGEPACK)
        ],
        auth_service: Auth,
    ) -> None:
        await auth_service.reset_password(data.to_dict())

    @post(
        "/log-in",
        status_code=200,
        response_model=auth.Tokens,
        media_type=MediaType.MESSAGEPACK,
    )
    async def log_in(
        self,
        data: Annotated[auth.LogIn, Body(media_type=RequestEncodingType.MESSAGEPACK)],
        request: Request,
        auth_service: Auth,
        mail_service: Mail,
    ) -> auth.Tokens:
        request_data = {
            "username": data.username,
            "password": data.password,
            "user_ip": request.headers.get("X-Forwarded-For", "Unknown").split(", ")[0],
            "user_agent": request.headers.get("User-Agent", "Unknown"),
        }
        login_data = await auth_service.log_in(request_data)

        if login_data.get("verified", False):
            del request_data["password"], request_data["user_agent"]
            request_data["browser"] = login_data["browser"]
            request_data["email"] = login_data["email"]
            await mail_service.log_in(request_data)

        tokens = {
            "access_token": login_data["access_token"],
            "refresh_token": login_data["refresh_token"],
        }
        return auth.Tokens(**tokens)

    @post("/log-out", status_code=204)
    async def log_out(self, request: Request, auth_service: Auth) -> None:
        access_token = validate_access_token(request)
        await auth_service.log_out(access_token)

    @post("/resend-verification-mail", status_code=204)
    async def resend_verification_mail(
        self, request: Request, auth_service: Auth, mail_service: Mail
    ) -> None:
        access_token = validate_access_token(request)
        verification_mail = await auth_service.resend_verification_mail(access_token)
        await mail_service.resend_verification_mail(verification_mail)

    @get(
        "/auth",
        status_code=200,
        response_model=auth.Auth,
        media_type=MediaType.MESSAGEPACK,
    )
    async def auth_user(self, request: Request, auth_service: Auth) -> auth.Auth:
        access_token = validate_access_token(request)
        user_info = await auth_service.auth(access_token)
        return auth.Auth(**user_info)

    @post(
        "/refresh",
        status_code=201,
        response_model=auth.Tokens,
        media_type=MediaType.MESSAGEPACK,
    )
    async def refresh(
        self,
        data: Annotated[
            auth.RefreshToken, Body(media_type=RequestEncodingType.MESSAGEPACK)
        ],
        request: Request,
        auth_service: Auth,
    ) -> auth.Tokens:
        request_data = {
            "refresh_token": data.refresh_token,
            "user_ip": request.headers.get("X-Forwarded-For", "Unknown").split(", ")[0],
            "user_agent": request.headers.get("User-Agent", "Unknown"),
        }
        tokens = await auth_service.refresh(request_data)
        return auth.Tokens(**tokens)

    @get(
        "/session-list",
        status_code=200,
        response_model=auth.SessionList,
        media_type=MediaType.MESSAGEPACK,
    )
    async def session_list(
        self, request: Request, auth_service: Auth
    ) -> auth.SessionList:
        access_token = validate_access_token(request)
        sessions = await auth_service.session_list(access_token)
        return auth.SessionList(
            tuple(auth.SessionInfo(**session) for session in sessions)
        )

    @post("/revoke-session", status_code=204)
    async def revoke_session(
        self,
        data: Annotated[
            auth.SessionId, Body(media_type=RequestEncodingType.MESSAGEPACK)
        ],
        request: Request,
        auth_service: Auth,
    ) -> None:
        request_data = {
            "access_token": validate_access_token(request),
            "session_id": str(data.session_id),
        }
        await auth_service.revoke_session(request_data)

    @get(
        "/profile",
        status_code=200,
        response_model=auth.Profile,
        media_type=MediaType.MESSAGEPACK,
    )
    async def profile(self, request: Request, auth_service: Auth) -> auth.Profile:
        access_token = validate_access_token(request)
        user_profile = await auth_service.profile(access_token)
        return auth.Profile(**user_profile)

    @patch("/update-email", status_code=204)
    async def update_email(
        self,
        data: Annotated[
            auth.UpdateEmail, Body(media_type=RequestEncodingType.MESSAGEPACK)
        ],
        request: Request,
        auth_service: Auth,
        mail_service: Mail,
    ) -> None:
        request_data = {
            "access_token": validate_access_token(request),
            "new_email": data.new_email,
        }
        verification_mail = await auth_service.update_email(request_data)
        await mail_service.update_email(verification_mail)

    @patch("/update-password", status_code=204)
    async def update_password(
        self,
        data: Annotated[
            auth.UpdatePassword, Body(media_type=RequestEncodingType.MESSAGEPACK)
        ],
        request: Request,
        auth_service: Auth,
    ) -> None:
        request_data = {
            "access_token": validate_access_token(request),
            "old_password": data.old_password,
            "new_password": data.new_password,
        }
        await auth_service.update_password(request_data)

    @delete("/delete-profile", status_code=204)
    async def delete_profile(
        self, request: Request, auth_service: Auth, files_service: Files
    ) -> None:
        access_token = validate_access_token(request)
        user_id = await auth_service.delete_profile(access_token)
        await files_service.delete_all_files(user_id)


auth_router = Router("/v1", route_handlers=(AuthController,), tags=("auth",))

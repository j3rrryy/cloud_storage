from typing import Generator

from proto import auth_pb2 as pb2

from .base import RPCBase


class Auth(RPCBase):
    @RPCBase.handle_exception
    async def register(self, data: dict[str, str]) -> dict[str, str]:
        request = pb2.RegisterRequest(**data)
        verification_mail = await self._stub.Register(request)
        return self.convert_to_dict(verification_mail)

    @RPCBase.handle_exception
    async def verify_email(self, verification_token: str) -> None:
        request = pb2.VerificationToken(verification_token=verification_token)
        await self._stub.VerifyEmail(request)

    @RPCBase.handle_exception
    async def request_reset_code(self, email: str) -> dict[str, str]:
        request = pb2.Email(email=email)
        reset_info = await self._stub.RequestResetCode(request)
        return self.convert_to_dict(reset_info)

    @RPCBase.handle_exception
    async def validate_code(self, data: dict[str, str]) -> bool:
        request = pb2.ResetCodeRequest(**data)
        validation_info = await self._stub.ValidateResetCode(request)
        return validation_info.is_valid

    @RPCBase.handle_exception
    async def reset_password(self, data: dict[str, str]) -> None:
        request = pb2.ResetPasswordRequest(**data)
        await self._stub.ResetPassword(request)

    @RPCBase.handle_exception
    async def log_in(self, data: dict[str, str]) -> dict[str, str]:
        request = pb2.LogInRequest(**data)
        login_data = await self._stub.LogIn(request)
        return self.convert_to_dict(login_data)

    @RPCBase.handle_exception
    async def log_out(self, access_token: str) -> None:
        request = pb2.AccessToken(access_token=access_token)
        await self._stub.LogOut(request)

    @RPCBase.handle_exception
    async def resend_verification_mail(self, access_token: str) -> dict[str, str]:
        request = pb2.AccessToken(access_token=access_token)
        verification_mail = await self._stub.ResendVerificationMail(request)
        return self.convert_to_dict(verification_mail)

    @RPCBase.handle_exception
    async def auth(self, access_token: str) -> dict[str, str]:
        request = pb2.AccessToken(access_token=access_token)
        user_info = await self._stub.Auth(request)
        converted = self.convert_to_dict(user_info)
        return converted

    @RPCBase.handle_exception
    async def refresh(self, data: dict[str, str]) -> dict[str, str]:
        request = pb2.RefreshRequest(**data)
        tokens = await self._stub.Refresh(request)
        return self.convert_to_dict(tokens)

    @RPCBase.handle_exception
    async def session_list(
        self, access_token: str
    ) -> Generator[dict[str, str], None, None]:
        request = pb2.AccessToken(access_token=access_token)
        sessions = await self._stub.SessionList(request)
        return (self.convert_to_dict(session) for session in sessions.sessions)

    @RPCBase.handle_exception
    async def revoke_session(self, data: dict[str, str]) -> None:
        request = pb2.RevokeSessionRequest(**data)
        await self._stub.RevokeSession(request)

    @RPCBase.handle_exception
    async def profile(self, access_token: str) -> dict[str, str | bool]:
        request = pb2.AccessToken(access_token=access_token)
        user_profile = await self._stub.Profile(request)
        converted = self.convert_to_dict(user_profile)
        return converted

    @RPCBase.handle_exception
    async def update_email(self, data: dict[str, str]) -> dict[str, str]:
        request = pb2.UpdateEmailRequest(**data)
        verification_mail = await self._stub.UpdateEmail(request)
        return self.convert_to_dict(verification_mail)

    @RPCBase.handle_exception
    async def update_password(self, data: dict[str, str]) -> None:
        request = pb2.UpdatePasswordRequest(**data)
        await self._stub.UpdatePassword(request)

    @RPCBase.handle_exception
    async def delete_profile(self, access_token: str) -> str:
        request = pb2.AccessToken(access_token=access_token)
        user_id = await self._stub.DeleteProfile(request)
        return user_id.user_id

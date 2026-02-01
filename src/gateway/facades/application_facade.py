from dto import auth_dto, file_dto
from protocols import ApplicationFacadeProtocol, AuthFacadeProtocol, FileFacadeProtocol


class ApplicationFacade(ApplicationFacadeProtocol):
    def __init__(
        self, auth_facade: AuthFacadeProtocol, file_facade: FileFacadeProtocol
    ):
        self._auth_facade = auth_facade
        self._file_facade = file_facade

    async def register(self, data: auth_dto.RegistrationDTO) -> None:
        await self._auth_facade.register(data)

    async def confirm_email(self, token: str) -> None:
        await self._auth_facade.confirm_email(token)

    async def request_reset_code(self, email: str) -> str:
        return await self._auth_facade.request_reset_code(email)

    async def validate_reset_code(self, data: auth_dto.ResetCodeDTO) -> bool:
        return await self._auth_facade.validate_reset_code(data)

    async def reset_password(self, data: auth_dto.ResetPasswordDTO) -> None:
        await self._auth_facade.reset_password(data)

    async def log_in(self, data: auth_dto.LogInDTO) -> auth_dto.LogInDataDTO:
        return await self._auth_facade.log_in(data)

    async def log_out(self, access_token: str) -> None:
        await self._auth_facade.log_out(access_token)

    async def resend_email_confirmation_mail(self, access_token: str) -> None:
        await self._auth_facade.resend_email_confirmation_mail(access_token)

    async def auth(self, access_token: str) -> str:
        return await self._auth_facade.auth(access_token)

    async def refresh(self, data: auth_dto.RefreshDTO) -> auth_dto.TokensDTO:
        return await self._auth_facade.refresh(data)

    async def session_list(self, access_token: str) -> list[auth_dto.SessionDTO]:
        return await self._auth_facade.session_list(access_token)

    async def revoke_session(self, data: auth_dto.RevokeSessionDTO) -> None:
        await self._auth_facade.revoke_session(data)

    async def profile(self, access_token: str) -> auth_dto.ProfileDTO:
        return await self._auth_facade.profile(access_token)

    async def update_email(self, data: auth_dto.UpdateEmailDTO) -> None:
        await self._auth_facade.update_email(data)

    async def update_password(self, data: auth_dto.UpdatePasswordDTO) -> None:
        await self._auth_facade.update_password(data)

    async def delete_profile(self, access_token: str) -> None:
        user_id = await self._auth_facade.delete_profile(access_token)
        await self._file_facade.delete_all(user_id)

    async def initiate_upload(
        self, access_token: str, data: file_dto.InitiateUploadDTO
    ) -> file_dto.InitiatedUploadDTO:
        user_id = await self.auth(access_token)
        dto = data.replace(user_id=user_id)
        return await self._file_facade.initiate_upload(dto)

    async def complete_upload(
        self, access_token: str, data: file_dto.CompleteUploadDTO
    ) -> None:
        user_id = await self.auth(access_token)
        dto = data.replace(user_id=user_id)
        await self._file_facade.complete_upload(dto)

    async def abort_upload(
        self, access_token: str, data: file_dto.AbortUploadDTO
    ) -> None:
        user_id = await self.auth(access_token)
        dto = data.replace(user_id=user_id)
        await self._file_facade.abort_upload(dto)

    async def file_list(self, access_token: str) -> list[file_dto.FileInfoDTO]:
        user_id = await self.auth(access_token)
        return await self._file_facade.file_list(user_id)

    async def download(self, access_token: str, data: file_dto.FileDTO) -> str:
        user_id = await self.auth(access_token)
        dto = data.replace(user_id=user_id)
        return await self._file_facade.download(dto)

    async def delete(self, access_token: str, data: file_dto.DeleteDTO) -> None:
        user_id = await self.auth(access_token)
        dto = data.replace(user_id=user_id)
        await self._file_facade.delete(dto)

    async def delete_all(self, access_token: str) -> None:
        user_id = await self.auth(access_token)
        await self._file_facade.delete_all(user_id)

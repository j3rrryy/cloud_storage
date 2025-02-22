from typing import Annotated
from uuid import UUID

from litestar import Controller, MediaType, Request, Router, delete, get, post
from litestar.enums import RequestEncodingType
from litestar.exceptions import PermissionDeniedException
from litestar.params import Body
from litestar.response import Redirect

from dto import files as files_dto
from schemas import files as fm
from services import Auth, Files
from utils import validate_access_token


class FilesController(Controller):
    path = "/files"

    @post(
        "/upload-file",
        status_code=201,
        response_model=fm.UploadURL,
        media_type=MediaType.MESSAGEPACK,
    )
    async def upload_file(
        self,
        data: Annotated[
            fm.UploadFile, Body(media_type=RequestEncodingType.MESSAGEPACK)
        ],
        request: Request,
        auth_service: Auth,
        files_service: Files,
    ) -> fm.UploadURL:
        access_token = validate_access_token(request)
        user_info = await auth_service.auth(access_token)

        if not user_info.verified:
            raise PermissionDeniedException(detail="Email not verified")

        dto = files_dto.UploadFileDTO(
            user_info.user_id, data.name, data.path, data.size
        )
        upload_url = await files_service.upload_file(dto)
        return fm.UploadURL(upload_url)

    @get(
        "/file-info/{file_id: uuid}",
        status_code=200,
        response_model=fm.FileInfo,
        media_type=MediaType.MESSAGEPACK,
    )
    async def file_info(
        self, file_id: UUID, request: Request, auth_service: Auth, files_service: Files
    ) -> fm.FileInfo:
        access_token = validate_access_token(request)
        user_info = await auth_service.auth(access_token)

        if not user_info.verified:
            raise PermissionDeniedException(detail="Email not verified")

        dto = files_dto.FileDTO(user_info.user_id, str(file_id))
        file_info = await files_service.file_info(dto)
        return fm.FileInfo(**file_info.dict())

    @get(
        "/file-list",
        status_code=200,
        response_model=fm.FileList,
        media_type=MediaType.MESSAGEPACK,
    )
    async def file_list(
        self, request: Request, auth_service: Auth, files_service: Files
    ) -> fm.FileList:
        access_token = validate_access_token(request)
        user_info = await auth_service.auth(access_token)

        if not user_info.verified:
            raise PermissionDeniedException(detail="Email not verified")

        files = await files_service.file_list(user_info.user_id)
        return fm.FileList(tuple(fm.FileInfo(**file.dict()) for file in files))

    @get("/download-file/{file_id: uuid}", status_code=200, response_class=Redirect)
    async def download_file(
        self, file_id: UUID, request: Request, auth_service: Auth, files_service: Files
    ) -> Redirect:
        access_token = validate_access_token(request)
        user_info = await auth_service.auth(access_token)

        if not user_info.verified:
            raise PermissionDeniedException(detail="Email not verified")

        dto = files_dto.FileDTO(user_info.user_id, str(file_id))
        file_url = await files_service.download_file(dto)
        return Redirect(file_url)

    @delete("/delete-files", status_code=204)
    async def delete_files(
        self,
        file_id: list[UUID],
        request: Request,
        auth_service: Auth,
        files_service: Files,
    ) -> None:
        access_token = validate_access_token(request)
        user_info = await auth_service.auth(access_token)

        if not user_info.verified:
            raise PermissionDeniedException(detail="Email not verified")

        dto = files_dto.DeleteFilesDTO(user_info.user_id, tuple(map(str, file_id)))
        await files_service.delete_files(dto)

    @delete("/delete-all-files", status_code=204)
    async def delete_all_files(
        self, request: Request, auth_service: Auth, files_service: Files
    ) -> None:
        access_token = validate_access_token(request)
        user_info = await auth_service.auth(access_token)

        if not user_info.verified:
            raise PermissionDeniedException(detail="Email not verified")

        await files_service.delete_all_files(user_info.user_id)


files_router = Router("/v1", route_handlers=(FilesController,), tags=("files",))

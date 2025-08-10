from typing import Annotated
from uuid import UUID

from litestar import Controller, MediaType, Request, Router, delete, get, post
from litestar.enums import RequestEncodingType
from litestar.params import Body
from litestar.response import Redirect

from dto import file_dto
from schemas import file_schemas
from service.v1 import AuthService, FileService
from utils import validate_access_token


class FileController(Controller):
    path = "/file"

    @post(
        "/upload-file",
        status_code=201,
        response_model=file_schemas.UploadURL,
        media_type=MediaType.MESSAGEPACK,
    )
    async def upload_file(
        self,
        data: Annotated[
            file_schemas.UploadFile, Body(media_type=RequestEncodingType.MESSAGEPACK)
        ],
        request: Request,
        auth_service_v1: AuthService,
        file_service_v1: FileService,
    ) -> file_schemas.UploadURL:
        access_token = validate_access_token(request)
        user_id = await auth_service_v1.auth(access_token)

        dto = file_dto.UploadFileDTO(user_id, data.name, data.path, data.size)
        upload_url = await file_service_v1.upload_file(dto)
        return file_schemas.UploadURL(upload_url)

    @get(
        "/file-info/{file_id: uuid}",
        status_code=200,
        response_model=file_schemas.FileInfo,
        media_type=MediaType.MESSAGEPACK,
    )
    async def file_info(
        self,
        file_id: UUID,
        request: Request,
        auth_service_v1: AuthService,
        file_service_v1: FileService,
    ) -> file_schemas.FileInfo:
        access_token = validate_access_token(request)
        user_id = await auth_service_v1.auth(access_token)

        dto = file_dto.FileDTO(user_id, str(file_id))
        file_info = await file_service_v1.file_info(dto)
        return file_schemas.FileInfo(**file_info.dict())

    @get(
        "/file-list",
        status_code=200,
        response_model=file_schemas.FileList,
        media_type=MediaType.MESSAGEPACK,
    )
    async def file_list(
        self,
        request: Request,
        auth_service_v1: AuthService,
        file_service_v1: FileService,
    ) -> file_schemas.FileList:
        access_token = validate_access_token(request)
        user_id = await auth_service_v1.auth(access_token)
        files = await file_service_v1.file_list(user_id)
        return file_schemas.FileList(
            tuple(file_schemas.FileInfo(**file.dict()) for file in files)
        )

    @get("/download-file/{file_id: uuid}", status_code=200, response_class=Redirect)
    async def download_file(
        self,
        file_id: UUID,
        request: Request,
        auth_service_v1: AuthService,
        file_service_v1: FileService,
    ) -> Redirect:
        access_token = validate_access_token(request)
        user_id = await auth_service_v1.auth(access_token)

        dto = file_dto.FileDTO(user_id, str(file_id))
        file_url = await file_service_v1.download_file(dto)
        return Redirect(file_url)

    @delete("/delete-files", status_code=204)
    async def delete_files(
        self,
        file_id: list[UUID],
        request: Request,
        auth_service_v1: AuthService,
        file_service_v1: FileService,
    ) -> None:
        access_token = validate_access_token(request)
        user_id = await auth_service_v1.auth(access_token)
        dto = file_dto.DeleteFilesDTO(user_id, {str(fid) for fid in file_id})
        await file_service_v1.delete_files(dto)

    @delete("/delete-all-files", status_code=204)
    async def delete_all_files(
        self,
        request: Request,
        auth_service_v1: AuthService,
        file_service_v1: FileService,
    ) -> None:
        access_token = validate_access_token(request)
        user_id = await auth_service_v1.auth(access_token)
        await file_service_v1.delete_all_files(user_id)


file_router = Router("/v1", route_handlers=(FileController,), tags=("file",))

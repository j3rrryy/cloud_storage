from typing import Annotated
from uuid import UUID

from litestar import Controller, MediaType, Request, Router, delete, get, post
from litestar.enums import RequestEncodingType
from litestar.params import Body
from litestar.response import Redirect
from litestar.status_codes import HTTP_307_TEMPORARY_REDIRECT

from dto import file_dto
from schemas import file_schemas
from service.v1 import AuthService, FileService
from utils import validate_access_token


class FileController(Controller):
    path = "/files"

    @post(
        "/initiate-upload",
        status_code=200,
        response_model=file_schemas.InitiatedUpload,
        media_type=MediaType.MESSAGEPACK,
    )
    async def initiate_upload(
        self,
        data: Annotated[
            file_schemas.InitiateUpload,
            Body(media_type=RequestEncodingType.MESSAGEPACK),
        ],
        request: Request,
        auth_service_v1: AuthService,
        file_service_v1: FileService,
    ) -> file_schemas.InitiatedUpload:
        access_token = validate_access_token(request)
        user_id = await auth_service_v1.auth(access_token)

        dto = file_dto.InitiateUploadDTO(user_id, data.name, data.size)
        upload = await file_service_v1.initiate_upload(dto)
        return upload.to_schema(file_schemas.InitiatedUpload)

    @post("/complete-upload", status_code=201)
    async def complete_upload(
        self,
        data: Annotated[
            file_schemas.CompleteUpload,
            Body(media_type=RequestEncodingType.MESSAGEPACK),
        ],
        request: Request,
        auth_service_v1: AuthService,
        file_service_v1: FileService,
    ) -> None:
        access_token = validate_access_token(request)
        user_id = await auth_service_v1.auth(access_token)
        dto = file_dto.CompleteUploadDTO(
            user_id,
            data.upload_id,
            [
                file_dto.CompletePartDTO(part.part_number, part.etag)
                for part in data.parts
            ],
        )
        await file_service_v1.complete_upload(dto)

    @delete("/abort-upload/{upload_id: uuid}", status_code=204)
    async def abort_upload(
        self,
        upload_id: UUID,
        request: Request,
        auth_service_v1: AuthService,
        file_service_v1: FileService,
    ) -> None:
        access_token = validate_access_token(request)
        user_id = await auth_service_v1.auth(access_token)
        dto = file_dto.AbortUploadDTO(user_id, str(upload_id))
        await file_service_v1.abort_upload(dto)

    @get(
        "/{file_id: uuid}",
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
        return file_info.to_schema(file_schemas.FileInfo)

    @get(
        "/",
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
            tuple(file.to_schema(file_schemas.FileInfo) for file in files)
        )

    @get("/download/{file_id: uuid}", status_code=307, response_class=Redirect)
    async def download(
        self,
        file_id: UUID,
        request: Request,
        auth_service_v1: AuthService,
        file_service_v1: FileService,
    ) -> Redirect:
        access_token = validate_access_token(request)
        user_id = await auth_service_v1.auth(access_token)

        dto = file_dto.FileDTO(user_id, str(file_id))
        file_url = await file_service_v1.download(dto)
        return Redirect(file_url, status_code=HTTP_307_TEMPORARY_REDIRECT)

    @delete("/", status_code=204)
    async def delete_file(
        self,
        file_id: list[UUID],
        request: Request,
        auth_service_v1: AuthService,
        file_service_v1: FileService,
    ) -> None:
        access_token = validate_access_token(request)
        user_id = await auth_service_v1.auth(access_token)
        dto = file_dto.DeleteDTO(user_id, {str(fid) for fid in file_id})
        await file_service_v1.delete(dto)

    @delete("/all", status_code=204)
    async def delete_all(
        self,
        request: Request,
        auth_service_v1: AuthService,
        file_service_v1: FileService,
    ) -> None:
        access_token = validate_access_token(request)
        user_id = await auth_service_v1.auth(access_token)
        await file_service_v1.delete_all(user_id)


file_router = Router("/v1", route_handlers=(FileController,), tags=("file",))

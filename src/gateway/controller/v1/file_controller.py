from typing import Annotated
from uuid import UUID

from litestar import Controller, MediaType, Request, Router, delete, get, post
from litestar.enums import RequestEncodingType
from litestar.params import Body
from litestar.response import Redirect
from litestar.status_codes import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_307_TEMPORARY_REDIRECT,
)

from dto import file_dto
from facades import ApplicationFacade
from schemas import file_schemas
from utils import validate_access_token


class FileController(Controller):
    path = "/files"

    @post(
        "/initiate-upload",
        status_code=HTTP_200_OK,
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
        application_facade: ApplicationFacade,
    ) -> file_schemas.InitiatedUpload:
        access_token = validate_access_token(request)
        user_id = await application_facade.auth(access_token)
        dto = file_dto.InitiateUploadDTO(user_id, data.name, data.size)
        upload = await application_facade.initiate_upload(dto)
        return upload.to_schema(file_schemas.InitiatedUpload)

    @post("/complete-upload", status_code=HTTP_201_CREATED)
    async def complete_upload(
        self,
        data: Annotated[
            file_schemas.CompleteUpload,
            Body(media_type=RequestEncodingType.MESSAGEPACK),
        ],
        request: Request,
        application_facade: ApplicationFacade,
    ) -> None:
        access_token = validate_access_token(request)
        user_id = await application_facade.auth(access_token)
        dto = file_dto.CompleteUploadDTO(
            user_id,
            data.upload_id,
            [
                file_dto.CompletePartDTO(part.part_number, part.etag)
                for part in data.parts
            ],
        )
        await application_facade.complete_upload(dto)

    @delete("/abort-upload/{upload_id: str}", status_code=HTTP_204_NO_CONTENT)
    async def abort_upload(
        self,
        upload_id: str,
        request: Request,
        application_facade: ApplicationFacade,
    ) -> None:
        access_token = validate_access_token(request)
        user_id = await application_facade.auth(access_token)
        dto = file_dto.AbortUploadDTO(user_id, upload_id)
        await application_facade.abort_upload(dto)

    @get(
        "/{file_id: uuid}",
        status_code=HTTP_200_OK,
        response_model=file_schemas.FileInfo,
        media_type=MediaType.MESSAGEPACK,
    )
    async def file_info(
        self,
        file_id: UUID,
        request: Request,
        application_facade: ApplicationFacade,
    ) -> file_schemas.FileInfo:
        access_token = validate_access_token(request)
        user_id = await application_facade.auth(access_token)
        dto = file_dto.FileDTO(user_id, str(file_id))
        file_info = await application_facade.file_info(dto)
        return file_info.to_schema(file_schemas.FileInfo)

    @get(
        "/",
        status_code=HTTP_200_OK,
        response_model=file_schemas.FileList,
        media_type=MediaType.MESSAGEPACK,
    )
    async def file_list(
        self,
        request: Request,
        application_facade: ApplicationFacade,
    ) -> file_schemas.FileList:
        access_token = validate_access_token(request)
        user_id = await application_facade.auth(access_token)
        files = await application_facade.file_list(user_id)
        return file_schemas.FileList(
            [file.to_schema(file_schemas.FileInfo) for file in files]
        )

    @get(
        "/download/{file_id: uuid}",
        status_code=HTTP_307_TEMPORARY_REDIRECT,
        response_class=Redirect,
    )
    async def download(
        self,
        file_id: UUID,
        request: Request,
        application_facade: ApplicationFacade,
    ) -> Redirect:
        access_token = validate_access_token(request)
        user_id = await application_facade.auth(access_token)
        dto = file_dto.FileDTO(user_id, str(file_id))
        file_url = await application_facade.download(dto)
        return Redirect(file_url, status_code=HTTP_307_TEMPORARY_REDIRECT)

    @delete("/", status_code=HTTP_204_NO_CONTENT)
    async def delete_file(
        self,
        file_id: list[UUID],
        request: Request,
        application_facade: ApplicationFacade,
    ) -> None:
        access_token = validate_access_token(request)
        user_id = await application_facade.auth(access_token)
        dto = file_dto.DeleteDTO(user_id, list({str(fid) for fid in file_id}))
        await application_facade.delete(dto)

    @delete("/all", status_code=HTTP_204_NO_CONTENT)
    async def delete_all(
        self,
        request: Request,
        application_facade: ApplicationFacade,
    ) -> None:
        access_token = validate_access_token(request)
        user_id = await application_facade.auth(access_token)
        await application_facade.delete_all(user_id)


file_router = Router("/v1", route_handlers=(FileController,), tags=("file",))

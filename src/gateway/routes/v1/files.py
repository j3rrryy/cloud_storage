from typing import Annotated
from uuid import UUID

from litestar import Controller, MediaType, Request, Router, delete, get, post
from litestar.di import Provide
from litestar.enums import RequestEncodingType
from litestar.exceptions import NotAuthorizedException, PermissionDeniedException
from litestar.params import Body
from litestar.response import Redirect

from schemas import files as fm
from services import Auth, Files, connect_auth_service, connect_files_service


class FilesController(Controller):
    path = "/files"
    dependencies = {
        "auth_service": Provide(connect_auth_service),
        "files_service": Provide(connect_files_service),
    }

    @post(
        "/upload-file",
        status_code=200,
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
        access_token = request.headers.get("Authorization")

        if not access_token:
            raise NotAuthorizedException(detail="Token is invalid")

        user_info = await auth_service.auth(access_token.split()[1])

        if not user_info.get("verified", False):
            raise PermissionDeniedException(detail="Email not verified")

        request_data = {
            "user_id": user_info["user_id"],
            "name": data.name,
            "path": data.path,
            "size": data.size,
        }
        upload_url = await files_service.upload_file(request_data)
        return fm.UploadURL(url=upload_url)

    @get(
        "/file-info/{file_id: uuid}",
        status_code=200,
        response_model=fm.FileInfo,
        media_type=MediaType.MESSAGEPACK,
    )
    async def file_info(
        self,
        file_id: UUID,
        request: Request,
        auth_service: Auth,
        files_service: Files,
    ) -> fm.FileInfo:
        access_token = request.headers.get("Authorization")

        if not access_token:
            raise NotAuthorizedException(detail="Token is invalid")

        user_info = await auth_service.auth(access_token.split()[1])

        if not user_info.get("verified", False):
            raise PermissionDeniedException(detail="Email not verified")

        request_data = {
            "user_id": user_info["user_id"],
            "file_id": str(file_id),
        }
        info = await files_service.file_info(request_data)
        return fm.FileInfo(**info)

    @get(
        "/file-list",
        status_code=200,
        response_model=fm.FileList,
        media_type=MediaType.MESSAGEPACK,
    )
    async def file_list(
        self,
        request: Request,
        auth_service: Auth,
        files_service: Files,
    ) -> fm.FileList:
        access_token = request.headers.get("Authorization")

        if not access_token:
            raise NotAuthorizedException(detail="Token is invalid")

        user_info = await auth_service.auth(access_token.split()[1])

        if not user_info.get("verified", False):
            raise PermissionDeniedException(detail="Email not verified")

        files = await files_service.file_list(user_info["user_id"])
        return fm.FileList(files=tuple(fm.FileInfo(**file) for file in files))

    @get("/download-file/{file_id: uuid}", status_code=200, response_class=Redirect)
    async def download_file(
        self,
        file_id: UUID,
        request: Request,
        auth_service: Auth,
        files_service: Files,
    ) -> Redirect:
        access_token = request.headers.get("Authorization")

        if not access_token:
            raise NotAuthorizedException(detail="Token is invalid")

        user_info = await auth_service.auth(access_token.split()[1])

        if not user_info.get("verified", False):
            raise PermissionDeniedException(detail="Email not verified")

        request_data = {
            "user_id": user_info["user_id"],
            "file_id": str(file_id),
        }
        file_url = await files_service.download_file(request_data)
        return Redirect(file_url)

    @delete("/delete-files", status_code=204)
    async def delete_files(
        self,
        file_id: list[UUID],
        request: Request,
        auth_service: Auth,
        files_service: Files,
    ) -> None:
        access_token = request.headers.get("Authorization")

        if not access_token:
            raise NotAuthorizedException(detail="Token is invalid")

        user_info = await auth_service.auth(access_token.split()[1])

        if not user_info.get("verified", False):
            raise PermissionDeniedException(detail="Email not verified")

        request_data = {
            "user_id": user_info["user_id"],
            "file_ids": tuple(map(str, file_id)),
        }
        await files_service.delete_files(request_data)

    @delete("/delete-all-files", status_code=204)
    async def delete_all_files(
        self,
        request: Request,
        auth_service: Auth,
        files_service: Files,
    ) -> None:
        access_token = request.headers.get("Authorization")

        if not access_token:
            raise NotAuthorizedException(detail="Token is invalid")

        user_info = await auth_service.auth(access_token.split()[1])

        if not user_info.get("verified", False):
            raise PermissionDeniedException(detail="Email not verified")

        await files_service.delete_all_files(user_info["user_id"])


files_router = Router(path="/v1", route_handlers=(FilesController,), tags=("files",))

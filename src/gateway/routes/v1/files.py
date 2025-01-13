from typing import Annotated
from uuid import UUID

from litestar import MediaType, Request, Router, delete, get, post
from litestar.di import Provide
from litestar.enums import RequestEncodingType
from litestar.exceptions import NotAuthorizedException, PermissionDeniedException
from litestar.params import Body
from litestar.response import Redirect

from config import load_config
from schemas import files as fm
from services import Auth, Files, connect_auth_service, connect_files_service

config = load_config()


@post(
    "/upload-file",
    status_code=200,
    response_model=fm.UploadURL,
    media_type=MediaType.MESSAGEPACK,
    dependencies={
        "auth_service": Provide(connect_auth_service),
        "files_service": Provide(connect_files_service),
    },
)
async def upload_file(
    data: Annotated[fm.UploadFile, Body(media_type=RequestEncodingType.MESSAGEPACK)],
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
    dependencies={
        "auth_service": Provide(connect_auth_service),
        "files_service": Provide(connect_files_service),
    },
)
async def file_info(
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
    dependencies={
        "auth_service": Provide(connect_auth_service),
        "files_service": Provide(connect_files_service),
    },
)
async def file_list(
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


@get(
    "/download-file/{file_id: uuid}",
    status_code=200,
    response_class=Redirect,
    dependencies={
        "auth_service": Provide(connect_auth_service),
        "files_service": Provide(connect_files_service),
    },
)
async def download_file(
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


@delete(
    "/delete-files",
    status_code=204,
    dependencies={
        "auth_service": Provide(connect_auth_service),
        "files_service": Provide(connect_files_service),
    },
)
async def delete_files(
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


@delete(
    "/delete-all-files",
    status_code=204,
    dependencies={
        "auth_service": Provide(connect_auth_service),
        "files_service": Provide(connect_files_service),
    },
)
async def delete_all_files(
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


files_router = Router(
    path="/v1/files",
    route_handlers=(
        upload_file,
        file_info,
        file_list,
        download_file,
        delete_files,
        delete_all_files,
    ),
    tags=("files",),
)

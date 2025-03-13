from grpc import StatusCode
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from dto import request as request_dto
from dto import response as response_dto
from utils import repository_exception_handler

from .models import File


class FileRepository:
    @classmethod
    @repository_exception_handler
    async def upload_file(
        cls, data: request_dto.UploadFileRequestDTO, *, session: AsyncSession
    ) -> None:
        new_file = File(**data.dict())
        session.add(new_file)

        try:
            await session.commit()
        except IntegrityError as exc:
            exc.args = (StatusCode.ALREADY_EXISTS, "File already exists")
            raise exc

    @classmethod
    @repository_exception_handler
    async def file_info(
        cls, data: request_dto.FileOperationRequestDTO, *, session: AsyncSession
    ) -> response_dto.FileInfoResponseDTO:
        file = await session.get(File, data.file_id)

        if not file or file.user_id != data.user_id:
            raise FileNotFoundError(StatusCode.NOT_FOUND, "File not found")

        return response_dto.FileInfoResponseDTO.from_model(file)

    @classmethod
    @repository_exception_handler
    async def file_list(
        cls, user_id: str, *, session: AsyncSession
    ) -> tuple[response_dto.FileInfoResponseDTO, ...]:
        files = (
            (await session.execute(select(File).filter(File.user_id == user_id)))
            .scalars()
            .all()
        )
        return tuple(
            response_dto.FileInfoResponseDTO.from_model(file) for file in files
        )

    @classmethod
    @repository_exception_handler
    async def delete_files(
        cls, data: request_dto.DeleteFilesRequestDTO, *, session: AsyncSession
    ) -> response_dto.DeleteFilesResponseDTO:
        files = {"user_id": data.user_id, "paths": []}

        for file_id in data.file_ids:
            file = await session.get(File, file_id)

            if not file or file.user_id != data.user_id:
                raise FileNotFoundError(StatusCode.NOT_FOUND, "File not found")

            files["paths"].append(file.path)
            await session.delete(file)

        await session.commit()
        return response_dto.DeleteFilesResponseDTO(**files)

    @classmethod
    @repository_exception_handler
    async def delete_all_files(cls, user_id: str, *, session: AsyncSession) -> None:
        await session.execute(delete(File).filter(File.user_id == user_id))
        await session.commit()

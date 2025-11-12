from grpc import StatusCode
from sqlalchemy import delete, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from dto import request as request_dto
from dto import response as response_dto
from exceptions import FileNameIsAlreadyTakenException, FileNotFoundException
from utils import with_transaction

from .models import File


class FileRepository:
    @staticmethod
    @with_transaction
    async def check_if_name_is_taken(
        data: request_dto.InitiateUploadRequestDTO, session: AsyncSession
    ) -> None:
        row_count = (
            await session.execute(
                select(func.count())
                .select_from(File)
                .where(File.user_id == data.user_id, File.name == data.name)
            )
        ).scalar_one()
        if row_count:
            raise FileNameIsAlreadyTakenException(
                StatusCode.ALREADY_EXISTS, "File name is already taken"
            )

    @staticmethod
    @with_transaction
    async def complete_upload(
        data: request_dto.InitiatedUploadRequestDTO, session: AsyncSession
    ) -> None:
        new_file = data.to_model(File)
        session.add(new_file)

        try:
            await session.commit()
        except IntegrityError as exc:
            exc.args = (StatusCode.ALREADY_EXISTS, "File already exists")
            raise exc

    @staticmethod
    @with_transaction
    async def file_info(
        data: request_dto.FileRequestDTO, session: AsyncSession
    ) -> response_dto.FileInfoResponseDTO:
        file = await session.get(File, data.file_id)

        if not file or file.user_id != data.user_id:
            raise FileNotFoundException(StatusCode.NOT_FOUND, "File not found")

        return response_dto.FileInfoResponseDTO.from_model(file)

    @staticmethod
    @with_transaction
    async def file_list(
        user_id: str, session: AsyncSession
    ) -> tuple[response_dto.FileInfoResponseDTO, ...]:
        files = (
            (await session.execute(select(File).filter(File.user_id == user_id)))
            .scalars()
            .all()
        )
        return tuple(
            response_dto.FileInfoResponseDTO.from_model(file) for file in files
        )

    @staticmethod
    @with_transaction
    async def validate_user_files(
        user_id: str, file_ids: list[str], session: AsyncSession
    ) -> None:
        row_count = (
            await session.execute(
                select(func.count())
                .select_from(File)
                .where(File.user_id == user_id, File.file_id.in_(file_ids))
            )
        ).scalar_one()
        if row_count != len(file_ids):
            raise FileNotFoundException(
                StatusCode.NOT_FOUND, "One or more files not found"
            )

    @staticmethod
    @with_transaction
    async def delete(
        data: request_dto.DeleteFilesRequestDTO, session: AsyncSession
    ) -> None:
        await session.execute(
            delete(File).where(
                File.user_id == data.user_id, File.file_id.in_(data.file_ids)
            )
        )
        await session.commit()

    @staticmethod
    @with_transaction
    async def delete_all(user_id: str, session: AsyncSession) -> None:
        await session.execute(delete(File).filter(File.user_id == user_id))
        await session.commit()

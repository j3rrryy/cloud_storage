from grpc import StatusCode
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from dto import request as request_dto
from dto import response as response_dto
from utils import with_transaction

from .models import File


class FileRepository:
    @staticmethod
    @with_transaction
    async def upload_file(
        data: request_dto.UploadFileRequestDTO, session: AsyncSession
    ) -> None:
        new_file = File(**data.dict())
        session.add(new_file)

        try:
            await session.commit()
        except IntegrityError as exc:
            exc.args = (StatusCode.ALREADY_EXISTS, "File already exists")
            raise exc

    @staticmethod
    @with_transaction
    async def file_info(
        data: request_dto.FileOperationRequestDTO, session: AsyncSession
    ) -> response_dto.FileInfoResponseDTO:
        file = await session.get(File, data.file_id)

        if not file or file.user_id != data.user_id:
            raise FileNotFoundError(StatusCode.NOT_FOUND, "File not found")

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
    async def get_file_list_to_delete(
        data: request_dto.DeleteFilesRequestDTO, session: AsyncSession
    ) -> response_dto.DeleteFilesResponseDTO:
        files = (
            (
                await session.execute(
                    select(File).where(
                        File.file_id.in_(data.file_ids), File.user_id == data.user_id
                    )
                )
            )
            .scalars()
            .all()
        )

        if len(files) != len(data.file_ids):
            raise FileNotFoundError(StatusCode.NOT_FOUND, "One or more files not found")

        return response_dto.DeleteFilesResponseDTO(
            user_id=data.user_id, paths=[file.path for file in files]
        )

    @staticmethod
    @with_transaction
    async def delete_files(
        data: request_dto.DeleteFilesRequestDTO, session: AsyncSession
    ) -> None:
        await session.execute(
            delete(File).where(
                File.file_id.in_(data.file_ids), File.user_id == data.user_id
            )
        )
        await session.commit()

    @staticmethod
    @with_transaction
    async def delete_all_files(user_id: str, session: AsyncSession) -> None:
        await session.execute(delete(File).filter(File.user_id == user_id))
        await session.commit()

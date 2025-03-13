from grpc import StatusCode
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from dto import request as request_dto
from dto import response as response_dto

from .models import File


class FileRepository:
    @classmethod
    async def upload_file(
        cls, data: request_dto.UploadFileRequestDTO, session: AsyncSession
    ) -> None:
        try:
            new_file = File(**data.dict())
            session.add(new_file)
            await session.commit()
        except IntegrityError as exc:
            await session.rollback()
            exc.args = (StatusCode.ALREADY_EXISTS, "File already exists")
            raise exc
        except Exception as exc:
            await session.rollback()
            exc.args = (StatusCode.INTERNAL, f"Internal database error, {exc}")
            raise exc

    @classmethod
    async def file_info(
        cls, data: request_dto.FileOperationRequestDTO, session: AsyncSession
    ) -> response_dto.FileInfoResponseDTO:
        try:
            file = await session.get(File, data.file_id)

            if not file or file.user_id != data.user_id:
                raise FileNotFoundError(StatusCode.NOT_FOUND, "File not found")

            return response_dto.FileInfoResponseDTO.from_model(file)
        except FileNotFoundError as exc:
            raise exc
        except Exception as exc:
            exc.args = (StatusCode.INTERNAL, f"Internal database error, {exc}")
            raise exc

    @classmethod
    async def file_list(
        cls, user_id: str, session: AsyncSession
    ) -> tuple[response_dto.FileInfoResponseDTO, ...]:
        try:
            files = (
                (await session.execute(select(File).filter(File.user_id == user_id)))
                .scalars()
                .all()
            )
            return tuple(
                response_dto.FileInfoResponseDTO.from_model(file) for file in files
            )
        except Exception as exc:
            exc.args = (StatusCode.INTERNAL, f"Internal database error, {exc}")
            raise exc

    @classmethod
    async def delete_files(
        cls, data: request_dto.DeleteFilesRequestDTO, session: AsyncSession
    ) -> response_dto.DeleteFilesResponseDTO:
        try:
            files = {"user_id": data.user_id, "paths": []}

            for file_id in data.file_ids:
                file = await session.get(File, file_id)

                if not file or file.user_id != data.user_id:
                    raise FileNotFoundError(StatusCode.NOT_FOUND, "File not found")

                files["paths"].append(file.path)
                await session.delete(file)

            await session.commit()
            return response_dto.DeleteFilesResponseDTO(**files)
        except FileNotFoundError as exc:
            await session.rollback()
            raise exc
        except Exception as exc:
            await session.rollback()
            exc.args = (StatusCode.INTERNAL, f"Internal database error, {exc}")
            raise exc

    @classmethod
    async def delete_all_files(cls, user_id: str, session: AsyncSession) -> None:
        try:
            await session.execute(delete(File).filter(File.user_id == user_id))
            await session.commit()
        except Exception as exc:
            await session.rollback()
            exc.args = (StatusCode.INTERNAL, f"Internal database error, {exc}")
            raise exc

from typing import cast

from sqlalchemy import CursorResult, delete, exists, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from dto import request as request_dto
from dto import response as response_dto
from exceptions import (
    FileAlreadyExistsException,
    FileNameIsAlreadyTakenException,
    FileNotFoundException,
)
from protocols import FileRepositoryProtocol
from utils import database_exception_handler

from .models import File


class FileRepository(FileRepositoryProtocol):
    def __init__(self, sessionmaker: async_sessionmaker[AsyncSession]):
        self._sessionmaker = sessionmaker

    @database_exception_handler
    async def check_if_name_is_taken(
        self, data: request_dto.InitiateUploadRequestDTO
    ) -> None:
        async with self._sessionmaker() as session:
            result = await session.execute(
                select(
                    exists().where(File.user_id == data.user_id, File.name == data.name)
                )
            )
        if result.scalar():
            raise FileNameIsAlreadyTakenException

    @database_exception_handler
    async def complete_upload(
        self, data: request_dto.InitiatedUploadRequestDTO
    ) -> None:
        new_file = data.to_model(File)
        try:
            async with self._sessionmaker.begin() as session:
                session.add(new_file)
        except IntegrityError:
            raise FileAlreadyExistsException

    @database_exception_handler
    async def file_list(self, user_id: str) -> list[response_dto.FileInfoResponseDTO]:
        async with self._sessionmaker() as session:
            files = (
                (await session.execute(select(File).where(File.user_id == user_id)))
                .scalars()
                .all()
            )
        return [response_dto.FileInfoResponseDTO.from_model(file) for file in files]

    @database_exception_handler
    async def file_name(self, user_id: str, file_id: str) -> str:
        async with self._sessionmaker() as session:
            name = (
                await session.execute(
                    select(File.name).where(
                        File.user_id == user_id, File.file_id == file_id
                    )
                )
            ).scalar_one_or_none()
        if not name:
            raise FileNotFoundException
        return name

    @database_exception_handler
    async def delete(self, data: request_dto.DeleteFilesRequestDTO) -> None:
        async with self._sessionmaker.begin() as session:
            result = await session.execute(
                delete(File).where(
                    File.user_id == data.user_id, File.file_id.in_(data.file_ids)
                )
            )
            result = cast(CursorResult, result)
            if (result.rowcount or 0) != len(data.file_ids):
                raise FileNotFoundException

    @database_exception_handler
    async def delete_all(self, user_id: str) -> list[str]:
        async with self._sessionmaker.begin() as session:
            deleted_file_ids = list(
                await session.scalars(
                    delete(File).where(File.user_id == user_id).returning(File.file_id)
                )
            )
        return deleted_file_ids

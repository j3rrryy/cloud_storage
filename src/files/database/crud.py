from grpc import StatusCode
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from .models import File


class CRUD:
    @classmethod
    async def upload_file(cls, data: dict[str, str], session: AsyncSession) -> None:
        async with session:
            try:
                new_file = File(**data)
                session.add(new_file)
                await session.commit()
            except IntegrityError as exc:
                await session.rollback()
                exc.args = (StatusCode.ALREADY_EXISTS, "File already exists")
                raise exc
            except Exception as exc:
                await session.rollback()
                exc.args = (StatusCode.INTERNAL, "Internal database error")
                raise exc

    @classmethod
    async def file_info(
        cls, data: dict[str, str], session: AsyncSession
    ) -> dict[str, str]:
        async with session:
            try:
                file = await session.get(File, data["file_id"])

                if not file:
                    raise FileNotFoundError(StatusCode.NOT_FOUND, "File not found")

                return file.columns_to_dict()
            except FileNotFoundError as exc:
                raise exc
            except Exception as exc:
                exc.args = (StatusCode.INTERNAL, "Internal database error")
                raise exc

    @classmethod
    async def file_list(
        cls, user_id: str, session: AsyncSession
    ) -> tuple[dict[str, str]]:
        async with session:
            try:
                files = (
                    (
                        await session.execute(
                            select(File).filter(File.user_id == user_id)
                        )
                    )
                    .scalars()
                    .all()
                )
                result = tuple(file.columns_to_dict() for file in files)
                return result
            except Exception as exc:
                exc.args = (StatusCode.INTERNAL, "Internal database error")
                raise exc

    @classmethod
    async def delete_files(
        cls, data: dict[str, str], session: AsyncSession
    ) -> tuple[str]:
        async with session:
            try:
                file_paths = []

                for file_id in data["file_ids"]:
                    file = await session.get(File, file_id)

                    if not file:
                        raise FileNotFoundError(StatusCode.NOT_FOUND, "File not found")

                    await session.delete(file)
                    file_paths.append(file.path)

                await session.commit()
                return tuple(file_paths)
            except FileNotFoundError as exc:
                await session.rollback()
                raise exc
            except Exception as exc:
                await session.rollback()
                exc.args = (StatusCode.INTERNAL, "Internal database error")
                raise exc

    @classmethod
    async def delete_all_files(cls, user_id: str, session: AsyncSession) -> None:
        async with session:
            try:
                await session.execute(delete(File).filter(File.user_id == user_id))
                await session.commit()
            except Exception as exc:
                await session.rollback()
                exc.args = (StatusCode.INTERNAL, "Internal database error")
                raise exc

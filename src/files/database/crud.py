from grpc import StatusCode
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from .models import File


class CRUD:
    @classmethod
    async def upload_file(
        cls, data: dict[str, str | int], session: AsyncSession
    ) -> None:
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
    async def file_info(cls, file_id: str, session: AsyncSession) -> dict[str, str]:
        try:
            file = await session.get(File, file_id)

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
        try:
            files = (
                (await session.execute(select(File).filter(File.user_id == user_id)))
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
    ) -> dict[str, str]:
        try:
            filenames = {"user_id": data["user_id"], "filenames": []}

            for file_id in data["file_ids"]:
                file = await session.get(File, file_id)

                if not file:
                    raise FileNotFoundError(StatusCode.NOT_FOUND, "File not found")

                filenames["filenames"].append(file.name)
                await session.delete(file)
            await session.commit()
            return filenames
        except FileNotFoundError as exc:
            await session.rollback()
            raise exc
        except Exception as exc:
            await session.rollback()
            exc.args = (StatusCode.INTERNAL, "Internal database error")
            raise exc

    @classmethod
    async def delete_all_files(cls, user_id: str, session: AsyncSession) -> None:
        try:
            await session.execute(delete(File).filter(File.user_id == user_id))
            await session.commit()
        except Exception as exc:
            await session.rollback()
            exc.args = (StatusCode.INTERNAL, "Internal database error")
            raise exc

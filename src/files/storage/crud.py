from typing import AsyncGenerator, AsyncIterator

import aiofiles as aof
import aiofiles.os as aos
from grpc import StatusCode

from config import Config, load_config
from errors import DirectoryNotFoundError


class CRUD:
    _config: Config = load_config()

    @classmethod
    async def upload_file(
        cls,
        chunk_iterator: AsyncIterator,
        data: dict[str, str],
    ) -> int | None:
        semaphore = cls._config.app.semaphore

        try:
            if await aos.path.exists(data["path"]):
                raise FileExistsError(StatusCode.ALREADY_EXISTS, "File already exists")

            if not await aos.path.exists(data["user_dir"]):
                await aos.mkdir(data["user_dir"])

            async with semaphore:
                async with aof.open(data["path"], "wb") as file:
                    async for chunk in chunk_iterator:
                        await file.write(chunk.chunk)

            file_size = (await aos.stat(data["path"])).st_size
            return file_size
        except FileExistsError as exc:
            raise exc
        except Exception as exc:
            exc.args = (StatusCode.INTERNAL, "Internal filesystem error")
            raise exc

    @classmethod
    async def download_file(cls, file_path: str) -> AsyncGenerator[bytes, None]:
        semaphore = cls._config.app.semaphore

        try:
            if not await aos.path.exists(file_path):
                raise FileNotFoundError(StatusCode.NOT_FOUND, "File not found")
            else:
                async with semaphore:
                    async with aof.open(file_path, "rb") as file:
                        while chunk := await file.read(65536):
                            yield chunk

        except FileNotFoundError as exc:
            raise exc
        except Exception as exc:
            exc.args = (StatusCode.INTERNAL, "Internal filesystem error")
            raise exc

    @classmethod
    async def delete_files(cls, file_paths: tuple[str]) -> None:
        try:
            for file_path in file_paths:
                if not await aos.path.exists(file_path):
                    raise FileNotFoundError(StatusCode.NOT_FOUND, "File not found")

                await aos.remove(file_path)
        except FileNotFoundError as exc:
            raise exc
        except Exception as exc:
            exc.args = (StatusCode.INTERNAL, "Internal filesystem error")
            raise exc

    @classmethod
    async def delete_all_files(cls, user_id: str) -> None:
        user_dir = f"files/{user_id}/"

        try:
            if not await aos.path.exists(user_dir):
                raise DirectoryNotFoundError(
                    StatusCode.NOT_FOUND, "Directory not found"
                )

            for file_path in await aos.scandir(user_dir):
                await aos.remove(file_path)

            await aos.rmdir(user_dir)
        except DirectoryNotFoundError as exc:
            raise exc
        except Exception as exc:
            exc.args = (StatusCode.INTERNAL, "Internal filesystem error")
            raise exc

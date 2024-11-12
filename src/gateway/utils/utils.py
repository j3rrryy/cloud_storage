from enum import Enum
from typing import AsyncGenerator

from litestar.datastructures import UploadFile

from proto import files_pb2 as pb2


class MailTypes(Enum):
    VERIFICATION = 0
    INFO = 1


async def chunk_generator(
    file: UploadFile, data: dict[str, str]
) -> AsyncGenerator[dict[str, str | bytes], None]:
    yield data

    while chunk := await file.read(5 * 1024 * 1024):
        yield {"chunk": chunk}

    await file.close()


async def converted_chunks_generator(
    chunk_generator: AsyncGenerator[dict[str, str | bytes], None]
) -> AsyncGenerator[pb2.UploadFileRequest, None]:
    async for chunk in chunk_generator:
        request = pb2.UploadFileRequest(**chunk)
        yield request

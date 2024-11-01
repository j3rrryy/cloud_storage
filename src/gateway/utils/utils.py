from collections.abc import AsyncIterator
from enum import Enum
from mimetypes import guess_type
from typing import AsyncGenerator

from litestar.datastructures import UploadFile

from proto import files_pb2 as pb2


class MailTypes(Enum):
    VERIFICATION = 0
    INFO = 1


class ChunkStream(AsyncIterator):
    __slots__ = ("_buffer", "file")

    def __init__(self, file):
        self._buffer = []
        self.file = aiter(file)

    def __aiter__(self) -> AsyncIterator:
        return self

    async def __anext__(self):
        try:
            chunk = await anext(self.file)
            self._buffer.append(chunk.chunk)
        except:
            pass

        if self._buffer:
            result_chunk = self._buffer.pop(0)
        else:
            raise StopIteration

        return result_chunk

    async def setup(self):
        chunk = await anext(self.file)
        self._buffer.append(chunk.chunk)


async def chunk_generator(
    file: UploadFile, data: dict[str, str]
) -> AsyncGenerator[dict[str, str | bytes], None]:
    yield data

    while chunk := await file.read(65536):
        yield {"chunk": chunk}

    await file.close()


async def converted_chunks_generator(
    chunk_generator: AsyncGenerator[dict[str, str | bytes], None]
) -> AsyncGenerator[pb2.UploadFileRequest, None]:
    async for chunk in chunk_generator:
        request = pb2.UploadFileRequest(**chunk)
        yield request


def uploading_file_info(name: str) -> dict[str, str | dict[str, str]]:
    file_info = {
        "media_type": guess_type(name)[0],
        "headers": {"Content-Disposition": f"attachment; filename={name}"},
    }
    return file_info

import asyncio
import logging
import math
from urllib.parse import urlparse
from uuid import uuid4

from dto import request as request_dto
from dto import response as response_dto
from protocols import FileStorageProtocol, S3ClientProtocol
from settings import Settings


class FileStorage(FileStorageProtocol):
    logger = logging.getLogger()

    def __init__(self, s3_client: S3ClientProtocol):
        self._s3_client = s3_client
        self._semaphore = asyncio.BoundedSemaphore(20)

    async def initiate_upload(
        self, data: request_dto.InitiateUploadRequestDTO
    ) -> response_dto.InitiateUploadResponseDTO:
        file_id = str(uuid4())
        upload_id = await self._s3_client.create_multipart_upload(file_id)

        part_count = math.ceil(data.size / Settings.UPLOAD_CHUNK_SIZE)
        part_size = min(data.size, Settings.UPLOAD_CHUNK_SIZE)

        parts = await asyncio.gather(
            *(
                self._generate_part_url(file_id, upload_id, i)
                for i in range(1, part_count + 1)
            )
        )
        return response_dto.InitiateUploadResponseDTO(
            file_id=file_id,
            upload_id=upload_id,
            part_size=part_size,
            parts=parts,
        )

    async def complete_upload(
        self, file_id: str, data: request_dto.CompleteUploadRequestDTO
    ) -> None:
        parts = sorted(
            [
                {"PartNumber": part.part_number, "ETag": part.etag}
                for part in data.parts
            ],
            key=lambda x: x["PartNumber"],
        )
        await self._s3_client.complete_multipart_upload(file_id, data.upload_id, parts)

    async def abort_upload(self, file_id: str, upload_id: str) -> None:
        await self._s3_client.abort_multipart_upload(file_id, upload_id)

    async def download(self, file_id: str, name: str) -> str:
        url = await self._s3_client.generate_download_presigned_url(file_id, name)
        parsed = urlparse(url)
        return f"{parsed.path}?{parsed.query}"

    async def delete(self, file_ids: list[str]) -> None:
        keys = [{"Key": file_id} for file_id in file_ids]
        batches = [keys[i : i + 1000] for i in range(0, len(keys), 1000)]
        results = await asyncio.gather(
            *(self._delete_batch(batch) for batch in batches),
            return_exceptions=True,
        )
        for r in results:
            if isinstance(r, Exception):
                self.logger.error(str(r))

    async def ping(self) -> None:
        await self._s3_client.ping()

    async def _generate_part_url(
        self, file_id: str, upload_id: str, part_number: int
    ) -> response_dto.UploadPartResponseDTO:
        async with self._semaphore:
            url = await self._s3_client.generate_upload_presigned_url(
                file_id, upload_id, part_number
            )
            parsed = urlparse(url)
            return response_dto.UploadPartResponseDTO(
                part_number, f"{parsed.path}?{parsed.query}"
            )

    async def _delete_batch(self, chunk: list[dict[str, str]]) -> None:
        async with self._semaphore:
            await self._s3_client.delete_objects(chunk)

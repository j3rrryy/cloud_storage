from typing import Protocol


class S3ClientProtocol(Protocol):
    async def create_multipart_upload(self, file_id: str) -> str: ...

    async def generate_upload_presigned_url(
        self, file_id: str, upload_id: str, part_number: int
    ) -> str: ...

    async def complete_multipart_upload(
        self, file_id: str, upload_id: str, parts: list[dict[str, int | str]]
    ) -> None: ...

    async def abort_multipart_upload(self, file_id: str, upload_id: str) -> None: ...

    async def generate_download_presigned_url(
        self, file_id: str, file_name: str
    ) -> str: ...

    async def delete_objects(self, objects: list[dict[str, str]]) -> None: ...

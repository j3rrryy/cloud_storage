from .file_repository import FileRepositoryProtocol
from .file_service import FileServiceProtocol
from .file_storage import FileStorageProtocol
from .s3_client import S3ClientProtocol

__all__ = [
    "FileRepositoryProtocol",
    "FileServiceProtocol",
    "FileStorageProtocol",
    "S3ClientProtocol",
]

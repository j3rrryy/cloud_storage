from functools import wraps

from aiobotocore import session
from types_aiobotocore_s3 import S3Client

from config import load_config

__all__ = ["get_client"]


def _get_client() -> S3Client:
    config = load_config()
    aiosession = session.get_session()
    client = aiosession.create_client(
        "s3",
        endpoint_url=f"http://{config.minio.host}:{config.minio.port}",
        use_ssl=False,
        aws_access_key_id=config.minio.access_key,
        aws_secret_access_key=config.minio.secret_key,
    )
    return client


def get_client(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        async with _get_client() as client:
            res = await func(*args, **kwargs, client=client)
            return res

    return wrapper

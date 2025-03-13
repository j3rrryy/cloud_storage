from functools import wraps

from aiosmtplib import SMTP

from config import load_config


def _get_smtp() -> SMTP:
    config = load_config().smtp
    smtp = SMTP(
        hostname=config.hostname,
        port=config.port,
        username=config.username,
        password=config.password,
        use_tls=True,
    )
    return smtp


_smtp = _get_smtp()


def get_smtp(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        async with _smtp as smtp:
            await func(*args, **kwargs, smtp=smtp)

    return wrapper

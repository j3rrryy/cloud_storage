from aiosmtplib import SMTP

from config import load_config


def get_smtp() -> SMTP:
    config = load_config().smtp
    smtp = SMTP(
        hostname=config.hostname,
        port=config.port,
        username=config.username,
        password=config.password,
        use_tls=True,
    )
    return smtp

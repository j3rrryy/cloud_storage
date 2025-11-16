from litestar.config.cors import CORSConfig

from settings import AppSettings


def setup_cors() -> CORSConfig:
    return CORSConfig(
        allow_origins=AppSettings.ALLOWED_ORIGINS,
        allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS", "HEAD", "TRACE"],
        allow_headers=["*"],
        allow_credentials=True,
    )

from litestar.config.cors import CORSConfig

from settings import Settings


def setup_cors() -> CORSConfig:
    return CORSConfig(
        allow_origins=Settings.ALLOWED_ORIGINS,
        allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS", "HEAD", "TRACE"],
        allow_headers=["*"],
        allow_credentials=True,
    )

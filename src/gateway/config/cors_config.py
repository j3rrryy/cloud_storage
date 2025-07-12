import os

from litestar.config.cors import CORSConfig


def setup_cors() -> CORSConfig:
    return CORSConfig(
        allow_origins=os.environ["ALLOWED_ORIGINS"].split(", "),
        allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS", "HEAD", "TRACE"],
        allow_headers=["*"],
        allow_credentials=True,
    )

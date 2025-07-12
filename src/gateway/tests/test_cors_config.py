import os

from litestar.config.cors import CORSConfig

from config import setup_cors


def test_setup_cors():
    cors_config = setup_cors()
    assert cors_config == CORSConfig(
        allow_origins=os.environ["ALLOWED_ORIGINS"].split(", "),
        allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS", "HEAD", "TRACE"],
        allow_headers=["*"],
        allow_credentials=True,
    )

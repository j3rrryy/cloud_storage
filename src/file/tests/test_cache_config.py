import os
from unittest.mock import patch

from config import setup_cache


@patch("config.cache_config.cache")
def test_setup_cache(mock_cache):
    setup_cache()
    mock_cache.setup.assert_called_once_with(
        f"redis://{os.environ['REDIS_USER']}:{os.environ['REDIS_PASSWORD']}@"
        + f"{os.environ['REDIS_HOST']}:{os.environ['REDIS_PORT']}/{os.environ['REDIS_DB']}",
        client_side=True,
    )

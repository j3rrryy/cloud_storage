from unittest.mock import patch

from config import setup_cache
from settings import Settings


@patch("config.cache_config.cache")
def test_setup_cache(mock_cache):
    setup_cache()

    mock_cache.setup.assert_called_once_with(
        f"redis://{Settings.REDIS_USER}:{Settings.REDIS_PASSWORD}@"
        + f"{Settings.REDIS_HOST}:{Settings.REDIS_PORT}/{Settings.REDIS_DB}",
        client_side=True,
    )

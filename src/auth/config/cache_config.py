from cashews import cache

from settings import Settings


def setup_cache() -> None:
    cache.setup(
        f"redis://{Settings.REDIS_USER}:{Settings.REDIS_PASSWORD}@"
        + f"{Settings.REDIS_HOST}:{Settings.REDIS_PORT}/{Settings.REDIS_DB}",
        client_side=True,
    )

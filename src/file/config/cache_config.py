import os

from cashews import cache


def setup_cache() -> None:
    cache.setup(
        f"redis://{os.environ['REDIS_USER']}:{os.environ['REDIS_PASSWORD']}@"
        + f"{os.environ['REDIS_HOST']}:{os.environ['REDIS_PORT']}/{os.environ['REDIS_DB']}",
        client_side=True,
    )

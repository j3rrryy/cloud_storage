import os


class Settings:
    DEBUG: bool = bool(int(os.environ.get("DEBUG", "0")))
    ALLOWED_ORIGINS: list[str] = os.environ["ALLOWED_ORIGINS"].split(", ")

    AUTH_SERVICE: str = os.environ["AUTH_SERVICE"]
    FILE_SERVICE: str = os.environ["FILE_SERVICE"]
    KAFKA_SERVICE: str = os.environ["KAFKA_SERVICE"]

    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 2
    LIMIT_CONCURRENCY: int = 500
    LIMIT_MAX_REQUESTS: int = 50000

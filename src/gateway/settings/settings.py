import os


class Settings:
    APP_NAME = os.environ["APP_NAME"]
    VERSION = os.environ["VERSION"]
    DEBUG = bool(int(os.environ["DEBUG"]))
    ALLOWED_ORIGINS = os.environ["ALLOWED_ORIGINS"].split(", ")

    AUTH_SERVICE = os.environ["AUTH_SERVICE"]
    FILE_SERVICE = os.environ["FILE_SERVICE"]
    KAFKA_SERVICE = os.environ["KAFKA_SERVICE"]

    HOST = "0.0.0.0"
    PORT = 8000
    WORKERS = 2
    LIMIT_CONCURRENCY = 500
    LIMIT_MAX_REQUESTS = 50000

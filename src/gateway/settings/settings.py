import os


class Settings:
    APP_NAME = os.environ["APP_NAME"]
    VERSION = os.environ["VERSION"]
    DEBUG = bool(int(os.environ["DEBUG"]))
    ALLOWED_ORIGINS = os.environ["ALLOWED_ORIGINS"].split(",")

    AUTH_SERVICE = os.environ["AUTH_SERVICE"]
    FILE_SERVICE = os.environ["FILE_SERVICE"]
    KAFKA_SERVICE = os.environ["KAFKA_SERVICE"]
    GRPC_CHANNEL_READY_TIMEOUT = 5

    HOST = "0.0.0.0"
    PORT = 8000
    WORKERS = 1
    LIMIT_CONCURRENCY = 800
    LIMIT_MAX_REQUESTS = 50000

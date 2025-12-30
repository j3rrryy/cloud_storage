import os


class Settings:
    APP_NAME = os.environ["APP_NAME"]

    POSTGRES_DRIVER = "postgresql+asyncpg"
    POSTGRES_DB = os.environ["POSTGRES_DB"]
    POSTGRES_USER = os.environ["POSTGRES_USER"]
    POSTGRES_PASSWORD = os.environ["POSTGRES_PASSWORD"]
    POSTGRES_HOST = os.environ["POSTGRES_HOST"]
    POSTGRES_PORT = int(os.environ["POSTGRES_PORT"])

    REDIS_DB = int(os.environ["REDIS_DB"])
    REDIS_USER = os.environ["REDIS_USER"]
    REDIS_PASSWORD = os.environ["REDIS_PASSWORD"]
    REDIS_HOST = os.environ["REDIS_HOST"]
    REDIS_PORT = int(os.environ["REDIS_PORT"])

    MINIO_S3_BUCKET = os.environ["MINIO_S3_BUCKET"]
    MINIO_ROOT_USER = os.environ["MINIO_ROOT_USER"]
    MINIO_ROOT_PASSWORD = os.environ["MINIO_ROOT_PASSWORD"]
    MINIO_HOST = os.environ["MINIO_HOST"]
    MINIO_PORT = os.environ["MINIO_PORT"]

    MAX_FILE_SIZE = int(os.environ["MAX_FILE_SIZE"])
    UPLOAD_CHUNK_SIZE = int(os.environ["UPLOAD_CHUNK_SIZE"])

    GRPC_SERVER_ADDRESS = "[::]:50051"
    GRPC_SERVER_MAXIMUM_CONCURRENT_RPCS = 1000

    PROMETHEUS_SERVER_HOST = "0.0.0.0"
    PROMETHEUS_SERVER_PORT = 8000
    PROMETHEUS_SERVER_LIMIT_CONCURRENCY = 50
    PROMETHEUS_SERVER_LIMIT_MAX_REQUESTS = 10000

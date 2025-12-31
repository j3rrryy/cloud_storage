from grpc import StatusCode


class BaseException(Exception):
    status_code: StatusCode
    details: str


class BaseInternalException(BaseException):
    status_code = StatusCode.INTERNAL

    def __init__(self, service: str, exc: Exception):
        self.details = f"Internal {service} error: {exc}"


class DatabaseException(BaseInternalException):
    def __init__(self, exc: Exception):
        super().__init__("database", exc)


class StorageException(BaseInternalException):
    def __init__(self, exc: Exception):
        super().__init__("storage", exc)


class FileAlreadyExistsException(BaseException):
    status_code = StatusCode.ALREADY_EXISTS
    details = "File already exists"


class FileNotFoundException(BaseException):
    status_code = StatusCode.NOT_FOUND
    details = "File not found"


class FileNameIsAlreadyTakenException(BaseException):
    status_code = StatusCode.ALREADY_EXISTS
    details = "File name is already taken"


class FileTooLargeException(BaseException):
    status_code = StatusCode.INVALID_ARGUMENT
    details = "File too large"

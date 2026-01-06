from grpc import StatusCode


class BaseAppException(Exception):
    status_code: StatusCode
    details: str


class BaseInternalException(BaseAppException):
    status_code = StatusCode.INTERNAL

    def __init__(self, service: str, exc: Exception):
        self.details = f"Internal {service} error: {exc}"


class DatabaseException(BaseInternalException):
    def __init__(self, exc: Exception):
        super().__init__("database", exc)


class StorageException(BaseInternalException):
    def __init__(self, exc: Exception):
        super().__init__("storage", exc)


class FileNameIsAlreadyTakenException(BaseAppException):
    status_code = StatusCode.ALREADY_EXISTS
    details = "File name is already taken"


class FileAlreadyExistsException(BaseAppException):
    status_code = StatusCode.ALREADY_EXISTS
    details = "File already exists"


class FileNotFoundException(BaseAppException):
    status_code = StatusCode.NOT_FOUND
    details = "File not found"


class FileTooLargeException(BaseAppException):
    status_code = StatusCode.INVALID_ARGUMENT
    details = "File too large"

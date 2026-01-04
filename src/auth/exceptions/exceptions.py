from grpc import StatusCode


class BaseAppException(Exception):
    status_code: StatusCode
    details: str


class DatabaseException(BaseAppException):
    status_code = StatusCode.INTERNAL

    def __init__(self, exc: Exception):
        self.details = f"Internal database error: {exc}"


class UnauthenticatedException(BaseAppException):
    status_code = StatusCode.UNAUTHENTICATED

    def __init__(self, details: str):
        self.details = details


class EmailHasAlreadyBeenConfirmedException(BaseAppException):
    status_code = StatusCode.ALREADY_EXISTS
    details = "Email has already been confirmed"


class SessionNotFoundException(BaseAppException):
    status_code = StatusCode.NOT_FOUND
    details = "Session not found"

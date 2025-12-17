class NotFoundException(Exception):
    """Resource not found"""


class UnauthenticatedException(Exception):
    """Problems with authentication"""


class EmailHasAlreadyBeenConfirmedException(Exception):
    """Email has already been confirmed"""

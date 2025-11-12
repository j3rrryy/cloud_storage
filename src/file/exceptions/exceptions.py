class FileNameIsAlreadyTakenException(Exception):
    """File name is already taken"""


class FileTooLargeException(Exception):
    """File too large"""


class NoUploadedPartsException(Exception):
    """No uploaded parts"""


class FileNotFoundException(Exception):
    """File not found"""

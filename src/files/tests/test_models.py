from database import File

from .mocks import FILE_ID


def test_file():
    file = File(file_id=FILE_ID)
    assert str(file) == f"<File: {FILE_ID}>"

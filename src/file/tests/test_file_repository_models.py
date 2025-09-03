from repository import File

from .mocks import FILE_ID, FOLDER_ID


def test_folder():
    folder = File(folde_id=FOLDER_ID)
    assert str(folder) == f"<Folder: {FOLDER_ID}>"


def test_file():
    file = File(file_id=FILE_ID)
    assert str(file) == f"<File: {FILE_ID}>"

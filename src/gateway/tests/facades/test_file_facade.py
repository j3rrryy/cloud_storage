import pytest

from dto import file_dto

from ..mocks import USER_ID


@pytest.mark.asyncio
async def test_delete_with_no_files(file_facade, file_stub_v1):
    dto = file_dto.DeleteDTO(USER_ID, [])

    await file_facade.delete(dto)

    file_stub_v1.Delete.assert_not_called()

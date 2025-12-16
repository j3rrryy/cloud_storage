import pytest

from dto import auth_dto

from ..mocks import PASSWORD, USER_AGENT, USER_IP, USERNAME


@pytest.mark.asyncio
async def test_log_in_unverified(auth_stub_v1, auth_facade, producer):
    auth_stub_v1.LogIn.return_value.verified = False
    dto = auth_dto.LogInDTO(USERNAME, PASSWORD, USER_IP, USER_AGENT)

    await auth_facade.log_in(dto)

    producer.send.assert_not_called()

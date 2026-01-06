import pytest
from grpc import StatusCode

from dto import request as request_dto
from dto import response as response_dto
from exceptions import BaseAppException

from ..mocks import ACCESS_TOKEN, CODE, EMAIL, PASSWORD, TIMESTAMP, USER_ID, USERNAME


@pytest.mark.asyncio
async def test_validate_reset_code_invalid_code(auth_service):
    dto = request_dto.ResetCodeRequestDTO(USER_ID, CODE)

    is_valid = await auth_service.validate_reset_code(dto)

    assert not is_valid


@pytest.mark.asyncio
async def test_reset_password_code_is_not_validated(auth_service):
    dto = request_dto.ResetPasswordRequestDTO(USER_ID, PASSWORD)

    with pytest.raises(BaseAppException) as exc_info:
        await auth_service.reset_password(dto)

    assert exc_info.value.status_code == StatusCode.UNAUTHENTICATED
    assert exc_info.value.details == "Code is not validated"


@pytest.mark.asyncio
async def test_resend_email_confirmation_mail_already_confirmed(
    mocked_auth_repository, auth_service
):
    mocked_auth_repository.profile_by_user_id.return_value = (
        response_dto.ProfileResponseDTO(
            USER_ID, USERNAME, EMAIL, PASSWORD, True, TIMESTAMP
        )
    )

    with pytest.raises(BaseAppException) as exc_info:
        await auth_service.resend_email_confirmation_mail(ACCESS_TOKEN)

    assert exc_info.value.status_code == StatusCode.ALREADY_EXISTS
    assert exc_info.value.details == "Email has already been confirmed"

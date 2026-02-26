from unittest.mock import MagicMock

import pytest

from ..mocks import COUNTRY_CODE, USER_IP


@pytest.mark.asyncio
async def test_get_country_code(reader, geo_ip_service):
    reader.country = MagicMock()
    reader.country.return_value.country.iso_code = COUNTRY_CODE

    country_code = await geo_ip_service.get_country_code(USER_IP)

    assert country_code == COUNTRY_CODE


@pytest.mark.asyncio
async def test_get_country_code_no_code(reader, geo_ip_service):
    reader.country = MagicMock()
    reader.country.side_effect = Exception("Details")

    country_code = await geo_ip_service.get_country_code(USER_IP)

    assert country_code is None

from unittest.mock import MagicMock

import pytest

from ..mocks import EMAIL


@pytest.mark.asyncio
async def test_start_processing(application_facade):
    logger = MagicMock()
    application_facade.logger = logger

    await application_facade.start_processing()

    logger.info.assert_called_once_with(f"Sent EmailConfirmation mail to {EMAIL}")

from unittest.mock import AsyncMock

import pytest
from aiosmtplib import SMTP


@pytest.fixture
def mock_smtp() -> SMTP:
    return AsyncMock(spec=SMTP)

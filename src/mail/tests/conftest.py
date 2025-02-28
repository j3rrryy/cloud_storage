from unittest.mock import AsyncMock

import pytest
from aiosmtplib import SMTP


@pytest.fixture
def smtp() -> SMTP:
    return AsyncMock(spec=SMTP)

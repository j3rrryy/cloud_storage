from typing import Generator
from unittest.mock import AsyncMock

import inject
import pytest
from aiosmtplib import SMTP


@pytest.fixture
def mock_smtp() -> Generator[SMTP, None, None]:
    mock_smtp = AsyncMock(spec=SMTP)
    inject.clear_and_configure(lambda binder: binder.bind(SMTP, mock_smtp))
    yield mock_smtp
    inject.clear()

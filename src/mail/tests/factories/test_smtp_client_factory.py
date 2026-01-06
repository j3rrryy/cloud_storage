from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from factories import SMTPClientFactory


@pytest.mark.asyncio
async def test_smtp_client_factory_initialize_success():
    with (
        patch("factories.smtp_client_factory.SMTP") as mock_smtp,
        patch("factories.smtp_client_factory.SMTPAdapter") as mock_adapter,
    ):
        factory = SMTPClientFactory()
        mock_smtp_instance = AsyncMock()
        mock_smtp.return_value = mock_smtp_instance
        mock_adapter_instance = MagicMock()
        mock_adapter.return_value = mock_adapter_instance

        await factory.initialize()

        mock_smtp_instance.connect.assert_awaited_once()
        assert factory._smtp == mock_smtp_instance
        assert factory._smtp_client == mock_adapter_instance


@pytest.mark.asyncio
async def test_smtp_client_factory_initialize_exception():
    factory = SMTPClientFactory()
    with (
        patch("factories.smtp_client_factory.SMTP") as mock_smtp,
        patch.object(factory, "close", new_callable=AsyncMock) as mock_close,
    ):
        mock_smtp.return_value.connect.side_effect = Exception("Connection failed")

        with pytest.raises(Exception):
            await factory.initialize()

        mock_close.assert_awaited_once()


@pytest.mark.asyncio
async def test_smtp_client_factory_close():
    factory = SMTPClientFactory()
    mock_smtp = AsyncMock()
    factory._smtp = mock_smtp

    await factory.close()

    mock_smtp.quit.assert_awaited_once()
    assert factory._smtp is None
    assert factory._smtp_client is None


@pytest.mark.asyncio
async def test_smtp_client_factory_close_no_smtp():
    factory = SMTPClientFactory()

    await factory.close()

    assert factory._smtp is None
    assert factory._smtp_client is None


def test_smtp_client_factory_get_smtp_client():
    factory = SMTPClientFactory()
    mock_client = MagicMock()
    factory._smtp_client = mock_client

    result = factory.get_smtp_client()

    assert result == mock_client


def test_smtp_client_factory_get_smtp_client_not_initialized():
    factory = SMTPClientFactory()

    with pytest.raises(RuntimeError, match="SMTPClient not initialized"):
        factory.get_smtp_client()

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from factories import MailServiceFactory


@pytest.mark.asyncio
async def test_mail_service_factory_initialize_success():
    factory = MailServiceFactory()
    with (
        patch("factories.mail_service_factory.AIOKafkaProducer") as mock_producer,
        patch("factories.mail_service_factory.MailKafkaAdapter") as mock_adapter,
    ):
        mock_producer_instance = AsyncMock()
        mock_producer.return_value = mock_producer_instance
        mock_adapter_instance = MagicMock()
        mock_adapter.return_value = mock_adapter_instance

        await factory.initialize()

        mock_producer_instance.start.assert_awaited_once()
        assert factory._mail_producer == mock_producer_instance
        assert factory._mail_service == mock_adapter_instance


@pytest.mark.asyncio
async def test_mail_service_factory_initialize_exception():
    factory = MailServiceFactory()
    with (
        patch("factories.mail_service_factory.AIOKafkaProducer") as mock_producer,
        patch.object(factory, "close", new_callable=AsyncMock) as mock_close,
    ):
        mock_producer.start.side_effect = Exception("Connection failed")

        with pytest.raises(Exception):
            await factory.initialize()

        mock_close.assert_awaited_once()


@pytest.mark.asyncio
async def test_mail_service_factory_close():
    factory = MailServiceFactory()
    mock_producer = AsyncMock()
    factory._mail_producer = mock_producer

    await factory.close()

    mock_producer.stop.assert_awaited_once()
    assert factory._mail_producer is None
    assert factory._mail_service is None


@pytest.mark.asyncio
async def test_mail_service_factory_close_no_producer():
    factory = MailServiceFactory()

    await factory.close()

    assert factory._mail_producer is None
    assert factory._mail_service is None


def test_mail_service_factory_get_mail_service():
    factory = MailServiceFactory()
    mock_service = MagicMock()
    factory._mail_service = mock_service

    result = factory.get_mail_service()

    assert result == mock_service


def test_mail_service_factory_get_mail_service_not_initialized():
    factory = MailServiceFactory()

    with pytest.raises(RuntimeError, match="MailService not initialized"):
        factory.get_mail_service()

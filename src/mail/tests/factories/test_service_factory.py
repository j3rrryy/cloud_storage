from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from factories import ServiceFactory


@pytest.mark.asyncio
async def test_service_factory_initialize_success():
    service_factory = ServiceFactory()

    with (
        patch.object(
            service_factory._kafka_consumer_factory,
            "initialize",
            new_callable=AsyncMock,
        ) as mock_kafka_init,
        patch.object(
            service_factory._smtp_client_factory, "initialize", new_callable=AsyncMock
        ) as mock_smtp_init,
    ):
        await service_factory.initialize()

        mock_kafka_init.assert_awaited_once()
        mock_smtp_init.assert_awaited_once()


@pytest.mark.asyncio
async def test_service_factory_initialize_exception():
    service_factory = ServiceFactory()
    with (
        patch.object(
            service_factory._kafka_consumer_factory,
            "initialize",
            new_callable=AsyncMock,
        ) as mock_kafka_init,
        patch.object(
            service_factory._smtp_client_factory, "initialize", new_callable=AsyncMock
        ),
        patch.object(service_factory, "close", new_callable=AsyncMock) as mock_close,
    ):
        mock_kafka_init.side_effect = Exception("Initialization failed")

        with pytest.raises(Exception):
            await service_factory.initialize()

        mock_close.assert_awaited_once()


@pytest.mark.asyncio
async def test_service_factory_close():
    service_factory = ServiceFactory()

    with (
        patch.object(
            service_factory._kafka_consumer_factory, "close", new_callable=AsyncMock
        ) as mock_kafka_close,
        patch.object(
            service_factory._smtp_client_factory, "close", new_callable=AsyncMock
        ) as mock_smtp_close,
    ):
        await service_factory.close()

        mock_kafka_close.assert_awaited_once()
        mock_smtp_close.assert_awaited_once()


def test_service_factory_get_kafka_consumer():
    service_factory = ServiceFactory()
    mock_consumer = MagicMock()

    with patch.object(
        service_factory._kafka_consumer_factory,
        "get_kafka_consumer",
        return_value=mock_consumer,
    ) as mock_get:
        result = service_factory.get_kafka_consumer()

        assert result == mock_consumer
        mock_get.assert_called_once()


def test_service_factory_get_smtp_client():
    service_factory = ServiceFactory()
    mock_client = MagicMock()

    with patch.object(
        service_factory._smtp_client_factory,
        "get_smtp_client",
        return_value=mock_client,
    ) as mock_get:
        result = service_factory.get_smtp_client()

        assert result == mock_client
        mock_get.assert_called_once()


def test_service_factory_get_application_facade():
    service_factory = ServiceFactory()
    mock_kafka_facade = MagicMock()
    mock_smtp_facade = MagicMock()
    mock_application_facade = MagicMock()

    with (
        patch.object(service_factory, "get_kafka_consumer"),
        patch.object(service_factory, "get_smtp_client"),
        patch("factories.service_factory.KafkaFacade", return_value=mock_kafka_facade),
        patch("factories.service_factory.SMTPFacade", return_value=mock_smtp_facade),
        patch(
            "factories.service_factory.ApplicationFacade",
            return_value=mock_application_facade,
        ) as mock_application_facade_class,
    ):
        result = service_factory.get_application_facade()

        assert result == mock_application_facade
        mock_application_facade_class.assert_called_once_with(
            mock_kafka_facade, mock_smtp_facade
        )


def test_service_factory_get_application_facade_cached():
    service_factory = ServiceFactory()
    mock_facade = MagicMock()
    service_factory._application_facade = mock_facade

    result = service_factory.get_application_facade()

    assert result == mock_facade


@pytest.mark.asyncio
async def test_service_factory_get_is_ready():
    service_factory = ServiceFactory()

    is_ready = await service_factory.get_is_ready()()

    assert not is_ready


@pytest.mark.asyncio
async def test_service_factory_get_is_ready_exception():
    service_factory = ServiceFactory()
    mock_is_ready = MagicMock()
    mock_is_ready.side_effect = Exception("Healthcheck timeout")
    service_factory._kafka_consumer_factory.is_ready = mock_is_ready

    is_ready = await service_factory.get_is_ready()()

    assert not is_ready

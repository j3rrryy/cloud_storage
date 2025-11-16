from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from factories import ServiceFactory


@pytest.mark.asyncio
async def test_service_factory_initialize_success():
    service_factory = ServiceFactory()

    with (
        patch.object(
            service_factory._auth_factory, "initialize", new_callable=AsyncMock
        ) as mock_auth_init,
        patch.object(
            service_factory._file_factory, "initialize", new_callable=AsyncMock
        ) as mock_file_init,
        patch.object(
            service_factory._mail_factory, "initialize", new_callable=AsyncMock
        ) as mock_mail_init,
    ):
        await service_factory.initialize()

        mock_auth_init.assert_awaited_once()
        mock_file_init.assert_awaited_once()
        mock_mail_init.assert_awaited_once()


@pytest.mark.asyncio
async def test_service_factory_initialize_exception():
    service_factory = ServiceFactory()
    with (
        patch.object(
            service_factory._auth_factory, "initialize", new_callable=AsyncMock
        ) as mock_auth_init,
        patch.object(
            service_factory._file_factory, "initialize", new_callable=AsyncMock
        ),
        patch.object(
            service_factory._mail_factory, "initialize", new_callable=AsyncMock
        ),
        patch.object(service_factory, "close", new_callable=AsyncMock) as mock_close,
    ):
        mock_auth_init.side_effect = Exception("Auth initialization failed")

        with pytest.raises(Exception):
            await service_factory.initialize()

        mock_close.assert_awaited_once()


@pytest.mark.asyncio
async def test_service_factory_close():
    service_factory = ServiceFactory()

    with (
        patch.object(
            service_factory._auth_factory, "close", new_callable=AsyncMock
        ) as mock_auth_close,
        patch.object(
            service_factory._file_factory, "close", new_callable=AsyncMock
        ) as mock_file_close,
        patch.object(
            service_factory._mail_factory, "close", new_callable=AsyncMock
        ) as mock_mail_close,
    ):
        await service_factory.close()

        mock_auth_close.assert_awaited_once()
        mock_file_close.assert_awaited_once()
        mock_mail_close.assert_awaited_once()


def test_service_factory_get_auth_service():
    service_factory = ServiceFactory()
    mock_service = MagicMock()

    with patch.object(
        service_factory._auth_factory, "get_auth_service", return_value=mock_service
    ) as mock_get:
        result = service_factory.get_auth_service()

        assert result == mock_service
        mock_get.assert_called_once()


def test_service_factory_get_file_service():
    service_factory = ServiceFactory()
    mock_service = MagicMock()

    with patch.object(
        service_factory._file_factory, "get_file_service", return_value=mock_service
    ) as mock_get:
        result = service_factory.get_file_service()

        assert result == mock_service
        mock_get.assert_called_once()


def test_service_factory_get_mail_service():
    service_factory = ServiceFactory()
    mock_service = MagicMock()

    with patch.object(
        service_factory._mail_factory, "get_mail_service", return_value=mock_service
    ) as mock_get:
        result = service_factory.get_mail_service()

        assert result == mock_service
        mock_get.assert_called_once()


def test_service_factory_get_application_facade():
    service_factory = ServiceFactory()
    mock_auth_service = MagicMock()
    mock_file_service = MagicMock()
    mock_mail_service = MagicMock()
    mock_facade = MagicMock()

    with (
        patch.object(
            service_factory, "get_auth_service", return_value=mock_auth_service
        ),
        patch.object(
            service_factory, "get_file_service", return_value=mock_file_service
        ),
        patch.object(
            service_factory, "get_mail_service", return_value=mock_mail_service
        ),
        patch(
            "factories.service_factory.ApplicationFacade", return_value=mock_facade
        ) as mock_facade_class,
    ):
        result = service_factory.get_application_facade()

        assert result == mock_facade
        mock_facade_class.assert_called_once_with(
            mock_auth_service, mock_file_service, mock_mail_service
        )


def test_service_factory_get_application_facade_cached():
    service_factory = ServiceFactory()
    mock_facade = MagicMock()
    service_factory._application_facade = mock_facade

    result = service_factory.get_application_facade()

    assert result == mock_facade

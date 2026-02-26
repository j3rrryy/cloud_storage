from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from factories import GeoIPServiceFactory


def test_geo_ip_service_factory_initialize_success():
    with (
        patch("factories.geo_ip_service_factory.Reader") as mock_reader,
        patch("factories.geo_ip_service_factory.GeoIPService") as mock_service,
    ):
        factory = GeoIPServiceFactory()
        mock_reader_instance = MagicMock()
        mock_reader.return_value = mock_reader_instance
        mock_service_instance = MagicMock()
        mock_service.return_value = mock_service_instance

        factory.initialize()

        assert factory._reader == mock_reader_instance
        assert factory._geo_ip_service == mock_service_instance


def test_geo_ip_service_factory_initialize_exception():
    factory = GeoIPServiceFactory()
    with (
        patch("factories.geo_ip_service_factory.Reader") as mock_reader,
        patch.object(factory, "close") as mock_close,
    ):
        mock_reader.side_effect = Exception("File not found")

        with pytest.raises(Exception):
            factory.initialize()

        mock_close.assert_called_once()


def test_geo_ip_service_factory_close():
    factory = GeoIPServiceFactory()
    mock_reader = MagicMock()
    factory._reader = mock_reader

    factory.close()

    mock_reader.close.assert_called_once()
    assert factory._reader is None
    assert factory._geo_ip_service is None


def test_geo_ip_service_factory_close_no_reader():
    factory = GeoIPServiceFactory()

    factory.close()

    assert factory._reader is None
    assert factory._geo_ip_service is None


def test_geo_ip_service_factory_get_geo_ip_service():
    factory = GeoIPServiceFactory()
    mock_service = MagicMock()
    factory._geo_ip_service = mock_service

    result = factory.get_geo_ip_service()

    assert result == mock_service


def test_geo_ip_service_factory_get_geo_ip_service_not_initialized():
    factory = GeoIPServiceFactory()

    with pytest.raises(RuntimeError, match="GeoIPService not initialized"):
        factory.get_geo_ip_service()


@pytest.mark.asyncio
async def test_geo_ip_service_factory_is_ready_success():
    factory = GeoIPServiceFactory()
    factory._reader = MagicMock()
    factory._geo_ip_service = AsyncMock()

    is_ready = await factory.is_ready()

    assert is_ready


@pytest.mark.asyncio
async def test_geo_ip_service_factory_is_ready_fail():
    factory = GeoIPServiceFactory()
    factory._reader = MagicMock()
    factory._geo_ip_service = AsyncMock()
    factory._reader.country.side_effect = Exception("Read error")

    is_ready = await factory.is_ready()

    assert not is_ready


@pytest.mark.asyncio
async def test_geo_ip_service_factory_is_ready_not_initialized():
    factory = GeoIPServiceFactory()

    is_ready = await factory.is_ready()

    assert not is_ready

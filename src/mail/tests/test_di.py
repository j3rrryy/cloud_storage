import asyncio
import os
from unittest.mock import AsyncMock, call, patch

import pytest
from aiokafka import AIOKafkaConsumer
from aiosmtplib import SMTP

from di import ConsumerManager, SMTPManager, configure_inject, setup_di
from enums import MailTypes


@pytest.mark.asyncio
@patch("di.di.SMTP")
async def test_smtp_manager_lifespan(mock_smtp):
    mock_connect = AsyncMock()
    mock_quit = AsyncMock()
    mock_smtp.return_value.connect = mock_connect
    mock_smtp.return_value.quit = mock_quit

    await SMTPManager.setup()
    mock_smtp.assert_called_with(
        hostname=os.environ["MAIL_HOSTNAME"],
        port=int(os.environ["MAIL_PORT"]),
        username=os.environ["MAIL_USERNAME"],
        password=os.environ["MAIL_PASSWORD"],
        use_tls=True,
        timeout=10,
    )
    mock_smtp.return_value.connect.assert_awaited()
    assert isinstance(SMTPManager._smtp_pool, asyncio.Queue)
    current_pool_size = SMTPManager._smtp_pool.qsize()
    assert current_pool_size == SMTPManager._pool_size
    assert SMTPManager._started

    await SMTPManager.close()
    mock_smtp.return_value.quit.assert_awaited()
    assert not SMTPManager._smtp_pool
    assert not SMTPManager._started


@pytest.mark.asyncio
@patch("di.di.SMTP")
async def test_smtp_manager_setup_already_started(mock_smtp):
    SMTPManager._started = True
    await SMTPManager.setup()

    mock_smtp.assert_not_called()
    assert SMTPManager._started


@pytest.mark.asyncio
@patch("di.di.SMTP")
@patch("di.di.SMTPManager.close")
async def test_smtp_manager_setup_exception(mock_close, mock_smtp):
    SMTPManager._started = False
    mock_smtp.side_effect = Exception("Details")

    with pytest.raises(Exception):
        await SMTPManager.setup()

    mock_close.assert_awaited_once()


@pytest.mark.asyncio
async def test_smtp_manager_close_already_closed():
    SMTPManager._smtp_pool = None

    await SMTPManager.close()
    assert not SMTPManager._smtp_pool
    assert not SMTPManager._started


@pytest.mark.asyncio
@patch("di.di.SMTP")
async def test_smtp_manager_close_exception(mock_smtp):
    SMTPManager._pool_size = 1
    SMTPManager._smtp_pool = asyncio.Queue()
    SMTPManager._smtp_pool.put_nowait(mock_smtp)
    mock_smtp.quit.side_effect = Exception("Details")

    await SMTPManager.close()
    assert not SMTPManager._smtp_pool
    assert not SMTPManager._started


@pytest.mark.asyncio
@patch("di.di.SMTP")
async def test_smtp_factory(mock_smtp):
    SMTPManager._started = True
    SMTPManager._smtp_pool = asyncio.Queue()
    SMTPManager._smtp_pool.put_nowait(mock_smtp)

    context = SMTPManager.smtp_factory()
    smtp = await context.__aenter__()
    assert smtp == mock_smtp
    assert not SMTPManager._smtp_pool.qsize()

    await context.__aexit__(None, None, None)
    assert SMTPManager._smtp_pool.qsize() == 1


@pytest.mark.asyncio
async def test_smtp_factory_not_initialized():
    SMTPManager._smtp_pool = None

    with pytest.raises(Exception) as exc_info:
        await SMTPManager.smtp_factory().__aenter__()

    assert exc_info.errisinstance(RuntimeError)
    assert exc_info.value.args == (
        "SMTP not initialized; SMTPManager.setup() was not called",
    )


@pytest.mark.asyncio
@patch("di.di.SMTP")
async def test_smtp_factory_not_connected(mock_smtp):
    SMTPManager._started = True
    SMTPManager._smtp_pool = asyncio.Queue()
    SMTPManager._smtp_pool.put_nowait(mock_smtp)
    mock_smtp.quit = AsyncMock()
    mock_smtp.return_value.connect = AsyncMock()
    mock_smtp.is_connected = False

    context = SMTPManager.smtp_factory()
    smtp = await context.__aenter__()
    assert smtp == mock_smtp.return_value
    assert not SMTPManager._smtp_pool.qsize()
    assert mock_smtp.return_value.connect.awaited_once()

    await context.__aexit__(None, None, None)
    assert SMTPManager._smtp_pool.qsize() == 1


@pytest.mark.asyncio
@patch("di.di.SMTP")
async def test_smtp_factory_exception(mock_smtp):
    SMTPManager._started = True
    SMTPManager._smtp_pool = asyncio.Queue()
    SMTPManager._smtp_pool.put_nowait(mock_smtp)
    mock_smtp.quit = AsyncMock()

    with pytest.raises(Exception):
        async with SMTPManager.smtp_factory():
            raise Exception("Details")

    assert SMTPManager._smtp_pool.qsize() == 1


@pytest.mark.asyncio
@patch("di.di.SMTP")
async def test_smtp_factory_double_exception(mock_smtp):
    SMTPManager._started = True
    SMTPManager._smtp_pool = asyncio.Queue()
    SMTPManager._smtp_pool.put_nowait(mock_smtp)
    mock_smtp.quit.side_effect = Exception("Quit details")

    with pytest.raises(Exception):
        async with SMTPManager.smtp_factory():
            raise Exception("Details")

    assert SMTPManager._smtp_pool.qsize() == 1


@pytest.mark.asyncio
@patch("di.di.AIOKafkaConsumer")
async def test_consumer_manager_lifespan(mock_consumer):
    mock_start = AsyncMock()
    mock_stop = AsyncMock()
    mock_consumer.return_value.start = mock_start
    mock_consumer.return_value.stop = mock_stop

    await ConsumerManager.setup()
    mock_consumer.assert_called_once_with(
        MailTypes.VERIFICATION.name,
        MailTypes.INFO.name,
        MailTypes.RESET.name,
        bootstrap_servers=os.environ["KAFKA_SERVICE"],
        group_id="mail",
        auto_offset_reset="earliest",
        max_poll_records=1000,
        request_timeout_ms=10000,
    )
    mock_start.assert_awaited_once()
    assert ConsumerManager.consumer == mock_consumer.return_value
    assert ConsumerManager._started

    await ConsumerManager.close()
    assert not ConsumerManager.consumer
    assert not ConsumerManager._started


@pytest.mark.asyncio
@patch("di.di.SMTP")
async def test_consumer_manager_setup_already_started(mock_smtp):
    ConsumerManager._started = True
    await ConsumerManager.setup()

    mock_smtp.assert_not_called()
    assert ConsumerManager._started


@pytest.mark.asyncio
@patch("di.di.AIOKafkaConsumer")
@patch("di.di.ConsumerManager.close")
async def test_consumer_manager_setup_exception(mock_close, mock_consumer):
    ConsumerManager._started = False
    mock_consumer.side_effect = Exception("Details")

    with pytest.raises(Exception):
        await ConsumerManager.setup()

    mock_close.assert_awaited_once()


@pytest.mark.asyncio
@patch("di.di.ConsumerManager.consumer")
async def test_consumer_manager_close_exception(mock_consumer):
    mock_consumer.stop.side_effect = Exception("Details")

    with pytest.raises(Exception):
        await ConsumerManager.close()

    assert not ConsumerManager.consumer
    assert not ConsumerManager._started


@pytest.mark.asyncio
@patch("di.di.ConsumerManager.consumer")
async def test_consumer_factory(mock_consumer):
    ConsumerManager._started = True
    consumer = ConsumerManager.consumer_factory()
    assert consumer == mock_consumer


@pytest.mark.asyncio
async def test_consumer_factory_not_initialized():
    ConsumerManager.consumer = None
    with pytest.raises(Exception) as exc_info:
        ConsumerManager.consumer_factory()

    assert exc_info.errisinstance(RuntimeError)
    assert exc_info.value.args == (
        "AIOKafkaConsumer not initialized; ConsumerManager.setup() was not called",
    )


@patch("di.di.inject.Binder")
@patch("di.di.SMTPManager")
@patch("di.di.ConsumerManager")
def test_configure_inject(mock_consumer_manager, mock_smtp_manager, mock_binder):
    configure_inject(mock_binder)

    expected_calls = [
        call(SMTP, mock_smtp_manager.smtp_factory),
        call(AIOKafkaConsumer, mock_consumer_manager.consumer_factory),
    ]

    mock_binder.bind_to_provider.assert_has_calls(expected_calls, any_order=True)
    assert mock_binder.bind_to_provider.call_count == 2


@pytest.mark.asyncio
@patch("di.di.SMTPManager")
@patch("di.di.ConsumerManager")
@patch("di.di.inject.configure")
@patch("di.di.configure_inject")
async def test_setup_di(
    mock_configure_inject,
    mock_inject_configure,
    mock_consumer_manager,
    mock_smtp_manager,
):
    mock_smtp_manager.setup = AsyncMock()
    mock_consumer_manager.setup = AsyncMock()
    await setup_di()

    mock_smtp_manager.setup.assert_awaited_once()
    mock_consumer_manager.setup.assert_awaited_once()
    mock_inject_configure.assert_called_once_with(mock_configure_inject, once=True)

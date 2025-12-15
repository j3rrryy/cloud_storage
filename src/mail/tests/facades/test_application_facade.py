import pytest


@pytest.mark.asyncio
async def test_start_processing(application_facade):
    await application_facade.start_processing()

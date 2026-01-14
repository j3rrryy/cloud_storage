from typing import Awaitable, Callable

from litestar import Controller, get
from litestar.exceptions import ServiceUnavailableException
from litestar.status_codes import HTTP_200_OK


class HealthController(Controller):
    path = "/health"

    @get("/live", status_code=HTTP_200_OK, include_in_schema=False)
    async def live(self) -> None:
        return

    @get("/ready", status_code=HTTP_200_OK, include_in_schema=False)
    async def ready(self, is_ready: Callable[[], Awaitable[bool]]) -> None:
        if not await is_ready():
            raise ServiceUnavailableException()

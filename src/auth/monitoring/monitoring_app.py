from typing import Awaitable, Callable

from prometheus_client import make_asgi_app


class MonitoringApp:
    def __init__(self, is_ready: Callable[[], Awaitable[bool]]):
        self._metrics_app = make_asgi_app()
        self._is_ready = is_ready

    async def __call__(self, scope, receive, send) -> None:
        if scope["type"] != "http":
            return

        match scope["path"]:
            case "/metrics":
                await self._metrics_app(scope, receive, send)
            case "/health/live":
                await self._respond(send, 200)
            case "/health/ready":
                await self._respond(send, 200 if await self._is_ready() else 503)
            case _:
                await self._respond(send, 404)

    async def _respond(self, send, status: int) -> None:
        await send({"type": "http.response.start", "status": status, "headers": []})
        await send({"type": "http.response.body", "body": b""})

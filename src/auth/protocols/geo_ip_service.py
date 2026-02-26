from typing import Protocol


class GeoIPServiceProtocol(Protocol):
    async def get_country_code(self, user_ip: str) -> str | None: ...
